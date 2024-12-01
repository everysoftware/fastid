from typing import Annotated

from fastapi import Depends

from app.main.config import main_settings
from app.oauth.config import (
    oauth_settings,
    google_settings,
    telegram_settings,
    yandex_settings,
)
from app.oauth.registry import ProviderRegistry
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth

registry = ProviderRegistry(
    base_authorization_url=oauth_settings.base_authorization_url,
    base_revoke_url=oauth_settings.base_revoke_url,
)


def get_registry() -> ProviderRegistry:
    return registry


RegistryDep = Annotated[ProviderRegistry, Depends(get_registry)]


google_oauth = GoogleOAuth(
    google_settings.client_id,
    google_settings.client_secret,
    f"{oauth_settings.base_redirect_url}/google",
)
yandex_oauth = YandexOAuth(
    yandex_settings.client_id,
    yandex_settings.client_secret,
    f"{oauth_settings.base_redirect_url}/yandex",
)
telegram_oauth = TelegramOAuth(
    telegram_settings.bot_token,
    redirect_uri=f"{main_settings.api_url}/oauth/redirect/telegram",
)


@registry.provider(
    "google",
    title="Google",
    icon="fa-google",
    color="#F44336",
    enabled=google_settings.enabled,
)
def get_google() -> GoogleOAuth:
    return google_oauth


@registry.provider(
    "telegram",
    title="Telegram",
    icon="fa-telegram",
    color="#03A9F4",
    enabled=telegram_settings.enabled,
)
def get_telegram() -> TelegramOAuth:
    return telegram_oauth


@registry.provider(
    "yandex",
    title="Yandex",
    icon="fa-yandex",
    color="#EA4335",
    enabled=yandex_settings.enabled,
)
def get_yandex() -> YandexOAuth:
    return yandex_oauth
