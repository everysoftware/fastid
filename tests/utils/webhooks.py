from typing import Any

from fastid.apps.schemas import AppDTO
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import WebhookEndpoint


async def create_webhook(uow: SQLAlchemyUOW, oauth_app: AppDTO, data: dict[str, Any]) -> WebhookEndpoint:
    record = WebhookEndpoint(app_id=oauth_app.id, **data)
    await uow.webhook_endpoints.add(record)
    await uow.commit()
    return record
