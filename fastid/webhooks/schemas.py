import datetime
from typing import Any

from pydantic import Field

from fastid.auth.schemas import UserDTO
from fastid.core.schemas import BaseModel
from fastid.webhooks.models import WebhookType


class SendWebhookRequest(BaseModel):
    type: WebhookType
    payload: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    event_type: WebhookType
    event_id: str
    timestamp: datetime.datetime


class WebhookPayload(BaseModel):
    event: Event
    data: dict[str, Any] = Field(default_factory=dict)


class Webhook(BaseModel):
    event: Event


class WebhookData(BaseModel):
    pass


class UserWebhookData(WebhookData):
    user: UserDTO


class UserWebhook(Webhook):
    data: UserWebhookData
