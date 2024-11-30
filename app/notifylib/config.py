from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class NotifierSettings(BaseSettings):
    from_name: str = "FastID"
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 465
    smtp_username: str
    smtp_password: str

    model_config = SettingsConfigDict(env_prefix="notifier_")


notifier_settings = NotifierSettings()
