from collections.abc import Mapping

from jinja2 import Environment, FileSystemLoader
from pydantic_settings import SettingsConfigDict

from fastid.auth.schemas import ContactType
from fastid.core.schemas import BaseSettings


class NotifySettings(BaseSettings):
    from_name: str = "FastID"
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 465
    smtp_username: str = "user@example.com"
    smtp_password: str = "password"

    telegram_enabled: bool = False

    contact_priority: Mapping[ContactType, int] = {ContactType.telegram: 0, ContactType.email: 1}

    model_config = SettingsConfigDict(env_prefix="notify_")


notify_settings = NotifySettings()

jinja_env = Environment(autoescape=True, loader=FileSystemLoader("templates"))
jinja_env.globals["from_name"] = notify_settings.from_name
