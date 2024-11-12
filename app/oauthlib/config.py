from pydantic_settings import SettingsConfigDict

from app.domain.schemas import BaseModel, BaseSettings


class OAuthSettingsMixin(BaseModel):
    oauth_allowed: bool = False
    client_id: str = ""
    client_secret: str = ""


class GoogleSettings(BaseSettings, OAuthSettingsMixin):
    model_config = SettingsConfigDict(env_prefix="google_")


class YandexSettings(BaseSettings, OAuthSettingsMixin):
    model_config = SettingsConfigDict(env_prefix="yandex_")


class TelegramSettings(BaseSettings, OAuthSettingsMixin):
    model_config = SettingsConfigDict(env_prefix="telegram_")
