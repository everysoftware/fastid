from typing import Annotated

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from fastid.auth.server import ServerURLDep
from fastid.core.config import core_settings
from fastid.core.urls import join_url_path
from fastid.integrations.config import integration_settings
from fastid.integrations.google.oauth import GoogleSSO
from fastid.integrations.registries import OAuth2Registry
from fastid.integrations.telegram.login import TelegramLoginWidget
from fastid.integrations.telegram.notifications import TelegramNotificationClient
from fastid.integrations.vk.oauth import VKSSO
from fastid.integrations.yandex.oauth import YandexSSO
from fastid.oauth.exceptions import OAuthProviderDisabledError


def get_google_sso(redirect_uri: str) -> GoogleSSO:
    if not integration_settings.google_oauth_enabled:
        raise OAuthProviderDisabledError
    return GoogleSSO(
        integration_settings.google_client_id,
        integration_settings.google_client_secret,
        redirect_uri,
    )


def get_yandex_sso(redirect_uri: str) -> YandexSSO:
    if not integration_settings.yandex_oauth_enabled:
        raise OAuthProviderDisabledError
    return YandexSSO(
        integration_settings.yandex_client_id,
        integration_settings.yandex_client_secret,
        redirect_uri,
    )


def get_vk_sso(redirect_uri: str) -> VKSSO:
    if not integration_settings.vk_oauth_enabled:
        raise OAuthProviderDisabledError
    return VKSSO(
        integration_settings.vk_client_id,
        integration_settings.vk_client_secret,
        redirect_uri,
    )


def get_registry(server_url: ServerURLDep) -> OAuth2Registry:
    registry = OAuth2Registry()
    callback_url = f"{server_url}{join_url_path(core_settings.api_path, 'oauth/callback')}"
    registry.provider("google")(lambda: get_google_sso(f"{callback_url}/google"))
    registry.provider("yandex")(lambda: get_yandex_sso(f"{callback_url}/yandex"))
    registry.provider("vk")(lambda: get_vk_sso(f"{callback_url}/vk"))
    return registry


OAuth2RegistryDep = Annotated[OAuth2Registry, Depends(get_registry)]


def get_telegram_widget(server_url: ServerURLDep) -> TelegramLoginWidget:
    oauth_url = f"{server_url}{join_url_path(core_settings.api_path, 'oauth')}"
    return TelegramLoginWidget(
        integration_settings.telegram_bot_token,
        f"{oauth_url}/redirect/telegram",
        f"{oauth_url}/callback/telegram",
    )


TelegramWidgetDep = Annotated[TelegramLoginWidget, Depends(get_telegram_widget)]


def get_bot() -> Bot:
    return Bot(integration_settings.telegram_bot_token, default=DefaultBotProperties(parse_mode="Markdown"))


def get_telegram_nc(bot: Annotated[Bot, Depends(get_bot)]) -> TelegramNotificationClient:
    return TelegramNotificationClient(bot)


TelegramNotificationsDep = Annotated[TelegramNotificationClient, Depends(get_telegram_nc)]
