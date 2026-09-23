from collections.abc import Sequence
from typing import Any

from sqlalchemy import select

from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification
from fastid.database.utils import UUIDv7
from fastid.webhooks.models import WebhookAttempt, WebhookDelivery, WebhookEndpoint, WebhookType


class WebhookEndpointRepository(SQLAlchemyRepository[WebhookEndpoint]):
    model_type = WebhookEndpoint

    async def get_active_for_type(self, webhook_type: WebhookType) -> Sequence[WebhookEndpoint]:
        stmt = WebhookEndpointTypeSpecification(webhook_type).apply(select(WebhookEndpoint))
        result = await self.session.scalars(stmt)
        return result.all()


class WebhookEndpointTypeSpecification(Specification):
    def __init__(self, webhook_type: WebhookType) -> None:
        self.type = webhook_type

    def apply(self, stmt: Any) -> Any:
        return stmt.where(WebhookEndpoint.type == self.type, WebhookEndpoint.is_active.is_(True))


class WebhookDeliveryRepository(SQLAlchemyRepository[WebhookDelivery]):
    model_type = WebhookDelivery


class WebhookAttemptRepository(SQLAlchemyRepository[WebhookAttempt]):
    model_type = WebhookAttempt


class WebhookDeliveryEndpointIDSpecification(Specification):
    def __init__(self, endpoint_id: UUIDv7) -> None:
        self.endpoint_id = endpoint_id

    def apply(self, stmt: Any) -> Any:
        return stmt.where(WebhookDelivery.endpoint_id == self.endpoint_id)
