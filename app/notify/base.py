from dataclasses import dataclass, field
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.auth.models import User
from app.notify.config import notify_settings

html_env = Environment(loader=FileSystemLoader("templates/notifications/html"), autoescape=True)
md_env = Environment(loader=FileSystemLoader("templates/notifications/md"), autoescape=True)

html_env.globals["from_name"] = notify_settings.from_name
md_env.globals["from_name"] = notify_settings.from_name


@dataclass
class Notification:
    user: User
    subject: str
    template: str
    method: str = "auto"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def user_telegram_id(self) -> int:
        assert self.user.telegram_id is not None, "User has no telegram_id"
        return self.user.telegram_id

    @property
    def user_email(self) -> str:
        assert self.user.email is not None, "User has no email"
        return self.user.email

    def as_html(self) -> str:
        template = html_env.get_template(f"{self.template}.html")
        return template.render(user=self.user, **self.extra)

    def as_markdown(self) -> str:
        template = md_env.get_template(f"{self.template}.md")
        return template.render(user=self.user, **self.extra)
