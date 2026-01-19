from typing import Any

from pydantic import Field

from fastid.core.schemas import BaseModel
from fastid.webhooks.models import WebhookType


class SendWebhookRequest(BaseModel):
    type: WebhookType
    payload: dict[str, Any] = Field(default_factory=dict)
