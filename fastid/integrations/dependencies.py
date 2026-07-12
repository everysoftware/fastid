from typing import Annotated

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from fastid.core.config import core_settings
from fastid.integrations.config import integration_settings
from fastid.integrations.google.oauth import GoogleSSO
from fastid.integrations.registries import OAuth2Registry
from fastid.integrations.telegram.login import TelegramLoginWidget
from fastid.integrations.telegram.notifications import TelegramNotificationClient
from fastid.integrations.vk.oauth import VKSSO
from fastid.integrations.yandex.oauth import YandexSSO
from fastid.oauth.exceptions import OAuthProviderDisabledError

registry = OAuth2Registry()


@registry.provider("google")
def get_google_sso() -> GoogleSSO:
    if not integration_settings.google_oauth_enabled:
        raise OAuthProviderDisabledError
    return GoogleSSO(
        integration_settings.google_client_id,
        integration_settings.google_client_secret,
        f"{integration_settings.base_redirect_url}/google",
    )


@registry.provider("yandex")
def get_yandex_sso() -> YandexSSO:
    if not integration_settings.yandex_oauth_enabled:
        raise OAuthProviderDisabledError
    return YandexSSO(
        integration_settings.yandex_client_id,
        integration_settings.yandex_client_secret,
        f"{integration_settings.base_redirect_url}/yandex",
    )


@registry.provider("vk")
def get_vk_sso() -> VKSSO:
    if not integration_settings.vk_oauth_enabled:
        raise OAuthProviderDisabledError
    return VKSSO(
        integration_settings.vk_client_id,
        integration_settings.vk_client_secret,
        f"{integration_settings.base_redirect_url}/vk",
    )


def get_registry() -> OAuth2Registry:
    return registry


OAuth2RegistryDep = Annotated[OAuth2Registry, Depends(get_registry)]


def get_telegram_widget() -> TelegramLoginWidget:
    return TelegramLoginWidget(
        integration_settings.telegram_bot_token,
        f"{core_settings.api_url}/oauth/redirect/telegram",
        f"{core_settings.api_url}/oauth/callback/telegram",
    )


TelegramWidgetDep = Annotated[TelegramLoginWidget, Depends(get_telegram_widget)]


def get_bot() -> Bot:
    return Bot(integration_settings.telegram_bot_token, default=DefaultBotProperties(parse_mode="Markdown"))


def get_telegram_nc(bot: Annotated[Bot, Depends(get_bot)]) -> TelegramNotificationClient:
    return TelegramNotificationClient(bot)


TelegramNotificationsDep = Annotated[TelegramNotificationClient, Depends(get_telegram_nc)]
