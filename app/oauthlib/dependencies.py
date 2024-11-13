from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Annotated, assert_never

from fastapi import Depends

from app.api.config import api_settings
from app.oauthlib.config import (
    google_settings,
    yandex_settings,
    telegram_settings,
)
from app.oauthlib.exceptions import ProviderNotAllowed
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.interfaces import IOAuth2
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth


class OAuthName(StrEnum):
    google = auto()
    yandex = auto()
    telegram = auto()


class OAuthFactory(ABC):
    @abstractmethod
    def create(self) -> IOAuth2: ...


class GoogleFactory(OAuthFactory):
    def create(self) -> IOAuth2:
        if not google_settings.oauth_allowed:
            raise ProviderNotAllowed()
        return GoogleOAuth(
            google_settings.client_id,
            google_settings.client_secret,
            f"{api_settings.oauth_callback_url}/google",
        )


class YandexFactory(OAuthFactory):
    def create(self) -> IOAuth2:
        if not yandex_settings.oauth_allowed:
            raise ProviderNotAllowed()
        return YandexOAuth(
            yandex_settings.client_id,
            yandex_settings.client_secret,
            f"{api_settings.oauth_callback_url}/yandex",
        )


class TelegramFactory(OAuthFactory):
    def create(self) -> IOAuth2:
        if not telegram_settings.oauth_allowed:
            raise ProviderNotAllowed()
        return TelegramOAuth(
            telegram_settings.client_secret,
            f"{api_settings.oauth_callback_url}/telegram",
        )


class OAuthPortal:
    @staticmethod
    def get_factory(name: OAuthName) -> OAuthFactory:
        match name:
            case OAuthName.google:
                return GoogleFactory()
            case OAuthName.yandex:
                return YandexFactory()
            case OAuthName.telegram:
                return TelegramFactory()
            case _:
                assert_never(name)


OAuthDep = Annotated[OAuthPortal, Depends()]
