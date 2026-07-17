from typing import Any

from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification
from fastid.database.utils import UUIDv7
from fastid.webhooks.models import Webhook, WebhookAttempt, WebhookDelivery, WebhookType


class WebhookRepository(SQLAlchemyRepository[Webhook]):
    model_type = Webhook


class WebhookTypeSpecification(Specification):
    def __init__(self, webhook_type: WebhookType) -> None:
        self.type = webhook_type

    def apply(self, stmt: Any) -> Any:
        return stmt.where(Webhook.type == self.type, Webhook.is_active.is_(True))


class WebhookDeliveryRepository(SQLAlchemyRepository[WebhookDelivery]):
    model_type = WebhookDelivery


class WebhookAttemptRepository(SQLAlchemyRepository[WebhookAttempt]):
    model_type = WebhookAttempt


class WebhookDeliveryWebhookIDSpecification(Specification):
    def __init__(self, webhook_id: UUIDv7) -> None:
        self.webhook_id = webhook_id

    def apply(self, stmt: Any) -> Any:
        return stmt.where(WebhookDelivery.webhook_id == self.webhook_id)
