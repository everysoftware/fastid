from typing import Any
from unittest.mock import AsyncMock

from starlette import status

from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook, WebhookType
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification
from fastid.webhooks.schemas import SendWebhookRequest
from fastid.webhooks.use_cases import WebhookUseCases
from tests.dependencies import get_test_cache, get_test_uow


async def test_webhook_delivery_releases_read_transaction(webhook_login: Webhook, uow: SQLAlchemyUOW) -> None:
    service = WebhookUseCases(get_test_uow(), get_test_cache(), AsyncMock())

    async def deliver(*args: Any, **kwargs: Any) -> Any:
        assert not service.uow.is_active
        assert not service.uow.session.in_transaction()
        return {"status_code": 202, "content": {"accepted": True}}

    service.sender.send = deliver
    await service.send(SendWebhookRequest(type=WebhookType.user_login, payload={"test": True}))
    event = await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_login.id))
    assert event.status_code == status.HTTP_202_ACCEPTED
