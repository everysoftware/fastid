from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseModel, BaseSettings


class OAuthSettings(BaseModel):
    oauth_allowed: bool = False
    client_id: str = ""
    client_secret: str = ""


class GoogleSettings(BaseSettings, OAuthSettings):
    model_config = SettingsConfigDict(env_prefix="google_")


class YandexSettings(BaseSettings, OAuthSettings):
    model_config = SettingsConfigDict(env_prefix="yandex_")


class TelegramSettings(BaseSettings, OAuthSettings):
    model_config = SettingsConfigDict(env_prefix="telegram_")


google_settings = GoogleSettings()
yandex_settings = YandexSettings()
telegram_settings = TelegramSettings()
