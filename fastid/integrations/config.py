from fastid.core.schemas import BaseSettings


class IntegrationSettings(BaseSettings):
    google_oauth_enabled: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""

    yandex_oauth_enabled: bool = False
    yandex_client_id: str = ""
    yandex_client_secret: str = ""

    vk_oauth_enabled: bool = False
    vk_client_id: str = ""
    vk_client_secret: str = ""

    telegram_widget_enabled: bool = False
    telegram_notification_enabled: bool = False
    telegram_bot_token: str = ""


integration_settings = IntegrationSettings()
