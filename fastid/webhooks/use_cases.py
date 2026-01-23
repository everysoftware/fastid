from fastid.core.base import UseCase
from fastid.database.dependencies import UOWRawDep, transactional
from fastid.security.webhooks import (
    generate_headers,
    get_event_id,
    get_timestamp,
    get_webhook_id,
)
from fastid.webhooks.models import WebhookEvent
from fastid.webhooks.repositories import WebhookTypeSpecification
from fastid.webhooks.schemas import Event, SendWebhookRequest, WebhookPayload
from fastid.webhooks.senders.dependencies import SenderDep


class WebhookUseCases(UseCase):
    def __init__(self, uow: UOWRawDep, sender: SenderDep) -> None:
        self.uow = uow  # Due to background nature of notification use cases, use raw dependency
        self.sender = sender

    @transactional
    async def send(self, dto: SendWebhookRequest) -> None:
        webhooks = await self.uow.webhooks.get_many(WebhookTypeSpecification(dto.type))
        event_id = get_event_id()
        event_timestamp = get_timestamp()
        event_dto = Event(event_type=dto.type, event_id=event_id, timestamp=event_timestamp)
        payload = WebhookPayload(event=event_dto, data=dto.payload).model_dump(mode="json")
        for webhook in webhooks.items:
            webhook_id = get_webhook_id()
            timestamp = get_timestamp()
            headers = generate_headers(payload, timestamp, str(webhook_id), webhook.secret)
            request = {"headers": headers, "body": payload}
            data = await self.sender.send(webhook.url, payload, headers)
            event = WebhookEvent(
                id=webhook_id,
                webhook_id=webhook.id,
                request=request,
                status_code=data["status_code"],
                response=data["content"],
            )
            await self.uow.webhook_events.add(event)
