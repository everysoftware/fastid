from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import BaseSettings


class NotifySettings(BaseSettings):
    from_name: str = "FastID"
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 465
    smtp_username: str = "user@example.com"
    smtp_password: str = "password"

    model_config = SettingsConfigDict(env_prefix="notify_")


notify_settings = NotifySettings()
