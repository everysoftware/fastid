from typing import Any

from fastid.apps.schemas import AppDTO
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook


async def create_webhook(uow: SQLAlchemyUOW, oauth_app: AppDTO, data: dict[str, Any]) -> Webhook:
    record = Webhook(app_id=oauth_app.id, **data)
    await uow.webhooks.add(record)
    await uow.commit()
    return record
