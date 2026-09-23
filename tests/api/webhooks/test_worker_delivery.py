import asyncio
from datetime import timedelta

import pytest
from httpx import AsyncClient
from starlette import status

import fastid.webhooks.worker as worker_module
from fastid.apps.schemas import AppDTO
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc
from fastid.security.webhooks import verify_standard_headers
from fastid.webhooks.config import webhook_settings
from fastid.webhooks.models import WebhookDeliveryStatus, WebhookEndpoint, WebhookType
from fastid.webhooks.repositories import WebhookDeliveryEndpointIDSpecification
from fastid.webhooks.senders.httpx import WebhookResponse, WebhookSender
from fastid.webhooks.worker import WebhookWorker
from tests.dependencies import get_test_uow
from tests.mocks import USER_CREATE

HTTP_MULTIPLE_CHOICES = 300
WORKER_CONCURRENCY = 2


class StubSender(WebhookSender):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.calls: list[tuple[bytes, dict[str, str]]] = []

    async def send(self, url: str, body: bytes, headers: dict[str, str]) -> WebhookResponse:
        assert url
        self.calls.append((body, headers))
        return WebhookResponse(
            status_code=self.status_code,
            content={"accepted": self.status_code < HTTP_MULTIPLE_CHOICES},
            error=None,
            retry_after_seconds=None,
            duration_ms=2,
        )


@pytest.mark.parametrize(
    ("status_code", "expected_status", "active"),
    [
        (204, WebhookDeliveryStatus.succeeded, True),
        (410, WebhookDeliveryStatus.cancelled, False),
        (500, WebhookDeliveryStatus.pending, True),
    ],
)
async def test_worker_records_delivery_outcome(  # noqa: PLR0913
    client: AsyncClient,
    webhook_registration: WebhookEndpoint,
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    expected_status: WebhookDeliveryStatus,
    *,
    active: bool,
) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)
    sender = StubSender(status_code)

    assert await WebhookWorker(sender=sender).run_once() == 1

    delivery = await uow.webhook_deliveries.find(WebhookDeliveryEndpointIDSpecification(webhook_registration.id))
    assert delivery.status == expected_status
    assert delivery.attempt_count == 1
    assert delivery.status_code == status_code
    attempts = (await uow.webhook_attempts.get_many()).items
    assert len(attempts) == 1
    body, headers = sender.calls[0]
    assert headers["webhook-id"] == str(delivery.id)
    assert headers["webhook-id"] != str(delivery.event_id)
    assert verify_standard_headers(body, headers, webhook_registration.secret)
    await uow.session.refresh(webhook_registration)
    assert webhook_registration.is_active is active


async def test_workers_do_not_claim_the_same_delivery(
    client: AsyncClient,
    webhook_registration: WebhookEndpoint,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)
    senders = [StubSender(204), StubSender(204)]

    counts = await asyncio.gather(*(WebhookWorker(sender=sender).run_once() for sender in senders))

    assert sum(counts) == 1
    assert sum(len(sender.calls) for sender in senders) == 1


async def test_worker_recovers_an_expired_lease(
    client: AsyncClient,
    webhook_registration: WebhookEndpoint,
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    delivery = await uow.webhook_deliveries.find(WebhookDeliveryEndpointIDSpecification(webhook_registration.id))
    delivery.status = WebhookDeliveryStatus.processing
    delivery.leased_until = naive_utc() - timedelta(seconds=1)
    await uow.commit()
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)

    assert await WebhookWorker(sender=StubSender(204)).run_once() == 1

    await uow.session.refresh(delivery)
    assert delivery.status == WebhookDeliveryStatus.succeeded


async def test_worker_claim_does_not_exceed_concurrency(
    client: AsyncClient,
    oauth_app: AppDTO,
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for index in range(5):
        await uow.webhook_endpoints.add(
            WebhookEndpoint(
                app_id=oauth_app.id,
                type=WebhookType.user_registration,
                url=f"https://example.com/webhooks/{index}",
            )
        )
    await uow.commit()
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)
    monkeypatch.setattr(webhook_settings, "worker_batch_size", 100)
    monkeypatch.setattr(webhook_settings, "worker_concurrency", WORKER_CONCURRENCY)

    claimed = await WebhookWorker(sender=StubSender(204))._claim()  # noqa: SLF001

    assert len(claimed) == WORKER_CONCURRENCY


async def test_stale_worker_cannot_record_after_delivery_is_reclaimed(
    client: AsyncClient,
    webhook_registration: WebhookEndpoint,
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)
    worker = WebhookWorker(sender=StubSender(204))

    first_claim = (await worker._claim(limit=1))[0]  # noqa: SLF001
    delivery = await uow.webhook_deliveries.find(WebhookDeliveryEndpointIDSpecification(webhook_registration.id))
    delivery.leased_until = naive_utc() - timedelta(seconds=1)
    await uow.commit()
    second_claim = (await worker._claim(limit=1))[0]  # noqa: SLF001

    assert first_claim.lease_token != second_claim.lease_token
    await worker._process(first_claim)  # noqa: SLF001

    await uow.session.refresh(delivery)
    assert delivery.status == WebhookDeliveryStatus.processing
    assert delivery.lease_token == second_claim.lease_token
    assert delivery.attempt_count == 0
    assert (await uow.webhook_attempts.get_many()).total == 0
