from enum import StrEnum, auto
from typing import Any
from uuid import UUID

from pydantic import Field

from fastid.auth.schemas import UserDTO
from fastid.core.schemas import BaseModel
from fastid.webhooks.models import WebhookType


class SignatureAlgorithm(StrEnum):
    sha256 = auto()
    sha512 = auto()
    sha1 = auto()


class SendWebhookRequest(BaseModel):
    type: WebhookType
    payload: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    event_type: WebhookType
    event_id: UUID
    timestamp: int


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
