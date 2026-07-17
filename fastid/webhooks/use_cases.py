from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.utils import naive_utc
from fastid.security.webhooks import get_event_id, get_timestamp, get_webhook_id
from fastid.webhooks.models import WebhookDeliveryStatus, WebhookEvent
from fastid.webhooks.repositories import WebhookTypeSpecification
from fastid.webhooks.schemas import Event, SendWebhookRequest, WebhookPayload


class WebhookUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def enqueue(self, dto: SendWebhookRequest) -> None:
        webhook_page = await self.uow.webhooks.get_many(WebhookTypeSpecification(dto.type))
        event_id = get_event_id()
        event_timestamp = get_timestamp()
        event_dto = Event(event_type=dto.type, event_id=event_id, timestamp=event_timestamp)
        payload = WebhookPayload(event=event_dto, data=dto.payload).model_dump(mode="json")
        now = naive_utc()
        for webhook in webhook_page.items:
            delivery = WebhookEvent(
                id=get_webhook_id(),
                webhook_id=webhook.id,
                event_id=event_id,
                event_type=dto.type,
                payload=payload,
                status=WebhookDeliveryStatus.pending,
                next_attempt_at=now,
            )
            await self.uow.webhook_events.add(delivery)

    async def send(self, dto: SendWebhookRequest) -> None:
        """Backward-compatible alias for enqueueing a durable delivery."""
        await self.enqueue(dto)
