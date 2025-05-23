from dataclasses import dataclass
from enum import StrEnum

from fastid.core.schemas import BaseModel
from fastid.notify.clients.schemas import Notification
from fastid.notify.config import notify_settings


class UnsafeAction(StrEnum):
    change_email = "change-email"
    change_password = "change-password"  # noqa: S105  # pragma: allowlist secret
    delete_account = "delete-account"
    recover_password = "recover-password"  # noqa: S105  # pragma: allowlist secret


class SendOTPRequest(BaseModel):
    action: UnsafeAction
    email: str | None = None


class VerifyOTPRequest(BaseModel):
    action: UnsafeAction
    code: str
    email: str | None = None


# Templates


@dataclass
class WelcomeNotification(Notification):
    subject: str = f"Welcome to {notify_settings.from_name}"
    template: str = "welcome"


@dataclass
class OTPNotification(Notification):
    email_override: str | None = None
    subject: str = "Your verification code"
    template: str = "code"

    @property
    def user_email(self) -> str:
        if self.email_override is not None:
            return self.email_override
        return super().user_email
