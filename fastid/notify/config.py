from collections.abc import Mapping

from jinja2 import Environment, FileSystemLoader
from pydantic_settings import SettingsConfigDict

from fastid.auth.schemas import ContactType
from fastid.core.schemas import BaseSettings


class NotifySettings(BaseSettings):
    app_name: str = "FastID"

    smtp_enabled: bool = False
    smtp_ssl: bool = False
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_from_email: str = "fastid@localhost"
    smtp_auth: bool = False
    smtp_username: str = "user@example.com"
    smtp_password: str = "password"

    telegram_enabled: bool = False

    contact_priority: Mapping[ContactType, int] = {ContactType.telegram: 0, ContactType.email: 1}

    @property
    def enabled(self) -> bool:
        return self.smtp_enabled or self.telegram_enabled

    @property
    def smtp_from(self) -> str:
        return f"{self.app_name} <{self.smtp_from_email}>"

    model_config = SettingsConfigDict(env_prefix="notify_")


notify_settings = NotifySettings()

jinja_env = Environment(autoescape=True, loader=FileSystemLoader("templates"))
jinja_env.globals["from_name"] = notify_settings.app_name
