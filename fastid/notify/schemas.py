from enum import StrEnum
from typing import Any

from pydantic import Field

from fastid.core.schemas import BaseModel


class UserAction(StrEnum):
    change_email = "change-email"
    change_password = "change-password"  # noqa: S105  # pragma: allowlist secret
    delete_account = "delete-account"
    recover_password = "recover-password"  # noqa: S105  # pragma: allowlist secret


class PushNotificationRequest(BaseModel):
    template: str
    context: dict[str, Any] = Field(default_factory=dict)


class SendOTPRequest(BaseModel):
    action: UserAction
    email: str | None = None


class VerifyOTPRequest(BaseModel):
    action: UserAction
    code: str
    email: str | None = None
