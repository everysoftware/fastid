from dataclasses import dataclass

from fastid.core.schemas import BaseModel
from fastid.notify.clients.schemas import Notification
from fastid.notify.config import notify_settings


class OTPRequest(BaseModel):
    new_email: str | None = None


class VerifyTokenRequest(BaseModel):
    code: str


# Templates


@dataclass
class WelcomeNotification(Notification):
    subject: str = f"Welcome to {notify_settings.from_name}"
    template: str = "welcome"


@dataclass
class VerificationNotification(Notification):
    new_email: str | None = None
    subject: str = "Your verification code"
    template: str = "code"

    @property
    def user_email(self) -> str:
        if self.new_email is not None:
            return self.new_email
        return super().user_email
