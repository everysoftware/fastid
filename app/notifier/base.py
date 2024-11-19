from dataclasses import dataclass, field
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Literal, Mapping

from jinja2 import Environment, FileSystemLoader

from app.auth.models import User
from app.notifier.config import notifier_settings

env = Environment(loader=FileSystemLoader("templates/mail"))
env.globals["app_title"] = notifier_settings.from_name


@dataclass
class Notification:
    user: User
    subject: str
    template: str
    method: Literal["email", "telegram", "auto"] = "auto"
    extra: dict[str, Any] = field(default_factory=dict)

    def as_html(self) -> str:
        return env.get_template(f"{self.template}.html").render(
            user=self.user, **self.extra
        )

    def as_email(self) -> Message:
        assert self.user.email is not None
        msg = MIMEMultipart("alternative")
        msg["From"] = notifier_settings.from_name
        msg["To"] = self.user.email
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.as_html(), "html"))
        return msg

    def as_telegram(self) -> Mapping[str, Any]:
        assert self.user.telegram_id is not None
        return {
            "chat_id": self.user.telegram_id,
            "text": self.as_html(),
            "parse_mode": "HTML",
        }
