from dataclasses import dataclass, field
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Literal, Mapping

from jinja2 import Environment, FileSystemLoader

from app.auth.models import User
from app.notifylib.config import notifier_settings

TemplateType = Literal["rich", "anemic"]


environments: Mapping[TemplateType, Environment] = {
    "rich": Environment(
        loader=FileSystemLoader("templates/notifications/rich")
    ),
    "anemic": Environment(
        loader=FileSystemLoader("templates/notifications/anemic")
    ),
}
for e in environments.values():
    e.globals["app_title"] = notifier_settings.from_name


@dataclass
class Notification:
    user: User
    subject: str
    template: str
    method: Literal["email", "telegram", "auto"] = "auto"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def user_telegram_id(self) -> int:
        assert self.user.telegram_id is not None, "User has no telegram_id"
        return self.user.telegram_id

    @property
    def user_email(self) -> str:
        assert self.user.email is not None, "User has no email"
        return self.user.email

    def as_html(self, template_type: TemplateType = "rich") -> str:
        return (
            environments[template_type]
            .get_template(f"{self.template}.html")
            .render(user=self.user, **self.extra)
        )

    def as_email(self) -> Message:
        msg = MIMEMultipart("alternative")
        msg["From"] = notifier_settings.from_name
        msg["To"] = self.user_email
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.as_html("rich"), "html"))
        return msg

    def as_telegram(self) -> Mapping[str, Any]:
        return {
            "chat_id": self.user_telegram_id,
            "text": self.as_html("anemic"),
            "parse_mode": "HTML",
        }
