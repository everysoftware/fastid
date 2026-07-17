import pytest
from httpx import AsyncClient
from starlette import status

from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook, WebhookDeliveryStatus
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification
from tests.mocks import USER_CREATE


async def test_wrong_url(client: AsyncClient, webhook_wrong_url: Webhook, uow: SQLAlchemyUOW) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED

    try:
        event = await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_wrong_url.id))
        assert event.status == WebhookDeliveryStatus.pending
        assert event.status_code is None
        assert event.attempt_count == 0
    except NoResultFoundError:
        pytest.fail("No webhook event created")
