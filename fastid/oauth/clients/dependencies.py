from typing import Annotated

from fastapi import Depends
from fastlink import GoogleSSO, TelegramSSO, YandexSSO

from fastid.core.config import main_settings
from fastid.oauth.clients.registry import SSORegistry
from fastid.oauth.config import (
    google_settings,
    oauth_settings,
    telegram_settings,
    yandex_settings,
)

registry = SSORegistry(
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
def get_google_sso() -> GoogleSSO:
    return GoogleSSO(
        google_settings.client_id,
        google_settings.client_secret,
        f"{oauth_settings.base_redirect_url}/google",
    )


@registry.provider(  # type: ignore[arg-type]
    "telegram",
    title="Telegram",
    icon="fa-telegram",
    color="#03A9F4",
    enabled=telegram_settings.oauth_enabled,
)
def get_telegram_sso() -> TelegramSSO:
    return TelegramSSO(
        telegram_settings.bot_token,
        f"{main_settings.api_url}/oauth/redirect/telegram",
        f"{main_settings.api_url}/oauth/callback/telegram",
    )


@registry.provider(
    "yandex",
    title="Yandex",
    icon="fa-yandex",
    color="#EA4335",
    enabled=yandex_settings.enabled,
)
def get_yandex_sso() -> YandexSSO:
    return YandexSSO(
        yandex_settings.client_id,
        yandex_settings.client_secret,
        f"{oauth_settings.base_redirect_url}/yandex",
    )


def get_registry() -> SSORegistry:
    return registry


RegistryDep = Annotated[SSORegistry, Depends(get_registry)]
