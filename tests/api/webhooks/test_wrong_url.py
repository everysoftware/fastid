import pytest
from httpx import AsyncClient
from starlette import status

from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook, WebhookDeliveryStatus
from fastid.webhooks.repositories import WebhookDeliveryWebhookIDSpecification
from tests.mocks import USER_CREATE


async def test_wrong_url(client: AsyncClient, webhook_wrong_url: Webhook, uow: SQLAlchemyUOW) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED

    try:
        delivery = await uow.webhook_deliveries.find(WebhookDeliveryWebhookIDSpecification(webhook_wrong_url.id))
        assert delivery.status == WebhookDeliveryStatus.pending
        assert delivery.status_code is None
        assert delivery.attempt_count == 0
    except NoResultFoundError:
        pytest.fail("No webhook delivery created")
