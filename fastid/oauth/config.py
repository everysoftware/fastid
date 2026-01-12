from pydantic_settings import SettingsConfigDict

from fastid.core.config import main_settings
from fastid.core.schemas import BaseModel, BaseSettings


class OAuthSettings(BaseModel):
    @property
    def base_authorization_url(self) -> str:
        return f"{main_settings.api_url}/oauth/login"

    @property
    def base_redirect_url(self) -> str:
        return f"{main_settings.api_url}/oauth/callback"

    @property
    def base_revoke_url(self) -> str:
        return f"{main_settings.api_url}/oauth/revoke"


class BaseOAuthSettings(BaseModel):
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""


class GoogleSettings(BaseSettings, BaseOAuthSettings):
    model_config = SettingsConfigDict(env_prefix="google_")


class YandexSettings(BaseSettings, BaseOAuthSettings):
    model_config = SettingsConfigDict(env_prefix="yandex_")


class TelegramSettings(BaseSettings):
    oauth_enabled: bool = False
    notification_enabled: bool = False
    bot_token: str = ""

    model_config = SettingsConfigDict(env_prefix="telegram_")


oauth_settings = OAuthSettings()
google_settings = GoogleSettings()
yandex_settings = YandexSettings()
telegram_settings = TelegramSettings()
