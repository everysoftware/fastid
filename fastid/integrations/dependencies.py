from typing import Annotated

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from fastid.auth.server import ServerURLDep
from fastid.core.config import core_settings
from fastid.core.urls import join_url_path
from fastid.database.dependencies import UOWDep
from fastid.integrations.config import integration_settings
from fastid.integrations.google.oauth import GoogleSSO
from fastid.integrations.registries import OAuth2Registry
from fastid.integrations.telegram.login import TelegramLoginWidget
from fastid.integrations.telegram.notifications import TelegramNotificationClient
from fastid.integrations.vk.oauth import VKSSO
from fastid.integrations.yandex.oauth import YandexSSO
from fastid.oauth.exceptions import OAuthProviderDisabledError
from fastid.oauth.models import OAuthProvider
from fastid.oauth.repositories import OAuthProviderNameSpecification


async def get_oauth_provider(uow: UOWDep, name: str) -> OAuthProvider:
    return await uow.oauth_providers.find(OAuthProviderNameSpecification(name))


async def get_telegram_provider(uow: UOWDep) -> OAuthProvider:
    return await get_oauth_provider(uow, "telegram")


TelegramProviderDep = Annotated[OAuthProvider, Depends(get_telegram_provider)]


def get_google_sso(redirect_uri: str, provider: OAuthProvider) -> GoogleSSO:
    if not provider.enabled:
        raise OAuthProviderDisabledError
    return GoogleSSO(
        provider.client_id,
        provider.client_secret,
        redirect_uri,
    )


def get_yandex_sso(redirect_uri: str, provider: OAuthProvider) -> YandexSSO:
    if not provider.enabled:
        raise OAuthProviderDisabledError
    return YandexSSO(
        provider.client_id,
        provider.client_secret,
        redirect_uri,
    )


def get_vk_sso(redirect_uri: str, provider: OAuthProvider) -> VKSSO:
    if not provider.enabled:
        raise OAuthProviderDisabledError
    return VKSSO(
        provider.client_id,
        provider.client_secret,
        redirect_uri,
    )


async def get_registry(server_url: ServerURLDep, uow: UOWDep) -> OAuth2Registry:
    registry = OAuth2Registry()
    callback_url = f"{server_url}{join_url_path(core_settings.api_path, 'oauth/callback')}"
    google = await get_oauth_provider(uow, "google")
    yandex = await get_oauth_provider(uow, "yandex")
    vk = await get_oauth_provider(uow, "vk")
    registry.provider("google")(lambda: get_google_sso(f"{callback_url}/google", google))
    registry.provider("yandex")(lambda: get_yandex_sso(f"{callback_url}/yandex", yandex))
    registry.provider("vk")(lambda: get_vk_sso(f"{callback_url}/vk", vk))
    return registry


OAuth2RegistryDep = Annotated[OAuth2Registry, Depends(get_registry)]


def build_telegram_widget(server_url: str, provider: OAuthProvider) -> TelegramLoginWidget:
    if not provider.enabled:
        raise OAuthProviderDisabledError
    oauth_url = f"{server_url}{join_url_path(core_settings.api_path, 'oauth')}"
    return TelegramLoginWidget(
        provider.client_secret,
        f"{oauth_url}/redirect/telegram",
        f"{oauth_url}/callback/telegram",
    )


def get_telegram_widget(server_url: ServerURLDep, provider: TelegramProviderDep) -> TelegramLoginWidget:
    return build_telegram_widget(server_url, provider)


TelegramWidgetDep = Annotated[TelegramLoginWidget, Depends(get_telegram_widget)]


def get_bot() -> Bot:
    return Bot(integration_settings.telegram_bot_token, default=DefaultBotProperties(parse_mode="Markdown"))


def get_telegram_nc(bot: Annotated[Bot, Depends(get_bot)]) -> TelegramNotificationClient:
    return TelegramNotificationClient(bot)


TelegramNotificationsDep = Annotated[TelegramNotificationClient, Depends(get_telegram_nc)]
