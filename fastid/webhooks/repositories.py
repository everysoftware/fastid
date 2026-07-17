from typing import Any

from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification
from fastid.database.utils import UUIDv7
from fastid.webhooks.models import Webhook, WebhookAttempt, WebhookEvent, WebhookType


class WebhookRepository(SQLAlchemyRepository[Webhook]):
    model_type = Webhook


class WebhookTypeSpecification(Specification):
    def __init__(self, webhook_type: WebhookType) -> None:
        self.type = webhook_type

    def apply(self, stmt: Any) -> Any:
        return stmt.where(Webhook.type == self.type, Webhook.is_active.is_(True))


class WebhookEventRepository(SQLAlchemyRepository[WebhookEvent]):
    model_type = WebhookEvent


class WebhookAttemptRepository(SQLAlchemyRepository[WebhookAttempt]):
    model_type = WebhookAttempt


class WebhookEventWebhookIDSpecification(Specification):
    def __init__(self, webhook_id: UUIDv7) -> None:
        self.webhook_id = webhook_id

    def apply(self, stmt: Any) -> Any:
        return stmt.where(WebhookEvent.webhook_id == self.webhook_id)
