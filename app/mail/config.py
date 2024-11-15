from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class MailSettings(BaseSettings):
    enabled: bool = False
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "FastAPI"

    model_config = SettingsConfigDict(env_prefix="mail_")


mail_settings = MailSettings()
