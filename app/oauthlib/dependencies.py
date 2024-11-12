from enum import StrEnum, auto
from typing import Annotated, cast

from fastapi import Depends

from app.oauthlib.exceptions import ProviderNotAllowed
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.interfaces import IOAuth2
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth
from app.runner.config import settings


class OAuthName(StrEnum):
    google = auto()
    yandex = auto()
    telegram = auto()


class OAuthRegistry:
    def __init__(self) -> None:
        self._google: IOAuth2 | None = None
        self._yandex: IOAuth2 | None = None
        self._telegram: IOAuth2 | None = None

    @property
    def google(self) -> IOAuth2:
        if not settings.google.oauth_allowed:
            raise ProviderNotAllowed()
        if self._google is None:
            self._google = GoogleOAuth(
                settings.google.client_id,
                settings.google.client_secret,
                f"{settings.oauth_callback_url}/google",
            )
        return self._google

    @property
    def yandex(self) -> IOAuth2:
        if not settings.yandex.oauth_allowed:
            raise ProviderNotAllowed()
        if self._yandex is None:
            self._yandex = YandexOAuth(
                settings.yandex.client_id,
                settings.yandex.client_secret,
                f"{settings.oauth_callback_url}/yandex",
            )
        return self._yandex

    @property
    def telegram(self) -> IOAuth2:
        if not settings.telegram.oauth_allowed:
            raise ProviderNotAllowed()
        if self._telegram is None:
            self._telegram = TelegramOAuth(
                settings.telegram.client_secret,
                f"{settings.oauth_callback_url}/telegram",
            )
        return self._telegram

    def get(self, name: OAuthName) -> IOAuth2:
        return cast(IOAuth2, getattr(self, name))


OAuthDep = Annotated[OAuthRegistry, Depends()]
