from fastid.core.schemas import BaseSettings


class IntegrationSettings(BaseSettings):
    telegram_notification_enabled: bool = False
    telegram_bot_token: str = ""


integration_settings = IntegrationSettings()
