import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import HttpUrl

from app.cache.config import CacheSettings
from app.db.config import DBSettings
from app.mail.config import MailSettings
from app.oauthlib.config import (
    GoogleSettings,
    YandexSettings,
    TelegramSettings,
)
from app.apps.config import OAuthSettings
from app.observability.config import ObservabilitySettings
from app.domain.schemas import BaseSettings
from app.authlib.config import AuthSettings

if not os.getenv("ENVIRONMENT_SET"):
    load_dotenv(".env")


class CORSSettings(BaseSettings):
    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_origin_regex: str | None = None


class AppSettings(BaseSettings):
    app_name: str = "fastapi"
    app_display_name: str = "FastAPI App"
    app_version: str = "0.1.0"
    app_env: Literal["dev", "prod"] = "dev"
    app_debug: bool = False
    app_domain: HttpUrl = HttpUrl("http://localhost:8000")

    @property
    def api_v1_url(self) -> HttpUrl:
        return HttpUrl(f"{self.app_domain}/api/v1")

    @property
    def oauth_callback_url(self) -> HttpUrl:
        return HttpUrl(f"{self.api_v1_url}/oauth/callback")

    oauth: OAuthSettings = OAuthSettings()
    cors: CORSSettings = CORSSettings()
    db: DBSettings = DBSettings()
    cache: CacheSettings = CacheSettings()
    obs: ObservabilitySettings = ObservabilitySettings()
    auth: AuthSettings = AuthSettings()
    mail: MailSettings = MailSettings()
    google: GoogleSettings = GoogleSettings()
    yandex: YandexSettings = YandexSettings()
    telegram: TelegramSettings = TelegramSettings()


settings = AppSettings()
