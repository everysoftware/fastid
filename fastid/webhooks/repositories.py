from typing import Any

from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification
from fastid.webhooks.models import Webhook, WebhookEvent, WebhookType


class WebhookRepository(SQLAlchemyRepository[Webhook]):
    model_type = Webhook


class WebhookTypeSpecification(Specification):
    def __init__(self, webhook_type: WebhookType) -> None:
        self.type = webhook_type

    def apply(self, stmt: Any) -> Any:
        return stmt.where(Webhook.type == self.type)


class WebhookEventRepository(SQLAlchemyRepository[WebhookEvent]):
    model_type = WebhookEvent
