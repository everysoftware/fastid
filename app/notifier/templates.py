from dataclasses import dataclass

from app.notifier.base import Notification
from app.notifier.config import notifier_settings


@dataclass
class WelcomeNotification(Notification):
    subject: str = f"Verify your account at {notifier_settings.from_name}"
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
