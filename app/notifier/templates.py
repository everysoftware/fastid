from dataclasses import dataclass

from app.notifier.base import Notification
from app.notifier.config import notifier_settings


@dataclass
class WelcomeNotification(Notification):
    subject: str = f"Verify your account at {notifier_settings.from_name}"
    template: str = "welcome"


@dataclass
class VerificationNotification(Notification):
    subject: str = "Your verification code"
    template: str = "code"
