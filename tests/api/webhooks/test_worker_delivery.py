import asyncio
from datetime import timedelta

import pytest
from httpx import AsyncClient
from starlette import status

import fastid.webhooks.worker as worker_module
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc
from fastid.security.webhooks import verify_standard_headers
from fastid.webhooks.models import Webhook, WebhookDeliveryStatus
from fastid.webhooks.repositories import WebhookDeliveryWebhookIDSpecification
from fastid.webhooks.senders.httpx import WebhookResponse, WebhookSender
from fastid.webhooks.worker import WebhookWorker
from tests.dependencies import get_test_uow
from tests.mocks import USER_CREATE

HTTP_MULTIPLE_CHOICES = 300


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
    webhook_registration: Webhook,
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

    delivery = await uow.webhook_deliveries.find(WebhookDeliveryWebhookIDSpecification(webhook_registration.id))
    assert delivery.status == expected_status
    assert delivery.attempt_count == 1
    assert delivery.status_code == status_code
    attempts = (await uow.webhook_attempts.get_many()).items
    assert len(attempts) == 1
    body, headers = sender.calls[0]
    assert verify_standard_headers(body, headers, webhook_registration.secret)
    await uow.session.refresh(webhook_registration)
    assert webhook_registration.is_active is active


async def test_workers_do_not_claim_the_same_delivery(
    client: AsyncClient,
    webhook_registration: Webhook,
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
    webhook_registration: Webhook,
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    delivery = await uow.webhook_deliveries.find(WebhookDeliveryWebhookIDSpecification(webhook_registration.id))
    delivery.status = WebhookDeliveryStatus.processing
    delivery.leased_until = naive_utc() - timedelta(seconds=1)
    await uow.commit()
    monkeypatch.setattr(worker_module, "get_uow_raw", get_test_uow)

    assert await WebhookWorker(sender=StubSender(204)).run_once() == 1

    await uow.session.refresh(delivery)
    assert delivery.status == WebhookDeliveryStatus.succeeded
