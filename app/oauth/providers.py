from typing import Annotated

from auth365.providers.google import GoogleOAuth
from auth365.providers.telegram import TelegramImplicitOAuth
from auth365.providers.yandex import YandexOAuth
from fastapi import Depends

from app.main.config import main_settings
from app.oauth.config import (
    google_settings,
    oauth_settings,
    telegram_settings,
    yandex_settings,
)
from app.oauth.registry import OAuth2Flow, ProviderRegistry

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
telegram_oauth = TelegramImplicitOAuth(
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
def get_google() -> OAuth2Flow:
    return google_oauth


@registry.provider(
    "telegram",
    title="Telegram",
    icon="fa-telegram",
    color="#03A9F4",
    enabled=telegram_settings.enabled,
)
def get_telegram() -> OAuth2Flow:
    return telegram_oauth


@registry.provider(
    "yandex",
    title="Yandex",
    icon="fa-yandex",
    color="#EA4335",
    enabled=yandex_settings.enabled,
)
def get_yandex() -> OAuth2Flow:
    return yandex_oauth
