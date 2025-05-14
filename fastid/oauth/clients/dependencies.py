from typing import Annotated

from fastapi import Depends
from fastlink import GoogleOAuth, TelegramAuth, YandexOAuth

from fastid.core.config import main_settings
from fastid.oauth.clients.registry import ProviderRegistry
from fastid.oauth.config import (
    google_settings,
    oauth_settings,
    telegram_settings,
    yandex_settings,
)

registry = ProviderRegistry(
    base_authorization_url=oauth_settings.base_authorization_url,
    base_revoke_url=oauth_settings.base_revoke_url,
)


@registry.provider(
    "google",
    title="Google",
    icon="fa-google",
    color="#F44336",
    enabled=google_settings.enabled,
)
def get_google() -> GoogleOAuth:
    return GoogleOAuth(
        google_settings.client_id,
        google_settings.client_secret,
        f"{oauth_settings.base_redirect_url}/google",
    )


@registry.provider(  # type: ignore[arg-type]
    "telegram",
    title="Telegram",
    icon="fa-telegram",
    color="#03A9F4",
    enabled=telegram_settings.enabled,
)
def get_telegram() -> TelegramAuth:
    return TelegramAuth(
        telegram_settings.bot_token,
        redirect_uri=f"{main_settings.api_url}/oauth/redirect/telegram",
    )


@registry.provider(
    "yandex",
    title="Yandex",
    icon="fa-yandex",
    color="#EA4335",
    enabled=yandex_settings.enabled,
)
def get_yandex() -> YandexOAuth:
    return YandexOAuth(
        yandex_settings.client_id,
        yandex_settings.client_secret,
        f"{oauth_settings.base_redirect_url}/yandex",
    )


def get_registry() -> ProviderRegistry:
    return registry


RegistryDep = Annotated[ProviderRegistry, Depends(get_registry)]
