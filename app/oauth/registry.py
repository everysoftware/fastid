from typing import MutableMapping, Callable

from app.base.schemas import BaseModel
from app.main.config import main_settings
from app.oauth.config import (
    google_settings,
    yandex_settings,
    telegram_settings,
    oauth_settings,
)
from app.oauth.exceptions import ProviderNotAllowed
from app.oauthlib.base import IOAuth2
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth


class ProviderMeta(BaseModel):
    name: str
    title: str
    icon: str
    color: str
    redirect_uri: str
    authorization_url: str
    revoke_url: str


class OAuthRegistry:
    def __init__(
        self,
        *,
        base_redirect_url: str,
        base_authorization_url: str,
        base_revoke_url: str,
    ) -> None:
        self.base_redirect_url = base_redirect_url
        self.base_authorization_url = base_authorization_url
        self.base_revoke_url = base_revoke_url

        self._meta: MutableMapping[str, ProviderMeta] = {}
        self._registry: MutableMapping[
            str, Callable[[ProviderMeta], IOAuth2]
        ] = {}

    @property
    def meta(self) -> MutableMapping[str, ProviderMeta]:
        return self._meta

    def provider(
        self, name: str, title: str, icon: str, color: str
    ) -> Callable[[Callable[[ProviderMeta], IOAuth2]], None]:
        def wrapper(factory: Callable[[ProviderMeta], IOAuth2]) -> None:
            meta = ProviderMeta(
                name=name,
                title=title,
                icon=icon,
                color=color,
                redirect_uri=f"{self.base_redirect_url}/{name}",
                authorization_url=f"{self.base_authorization_url}/{name}",
                revoke_url=f"{self.base_revoke_url}/{name}",
            )
            self._meta[name] = meta
            self._registry[name] = factory

        return wrapper

    def inspect(self, name: str) -> ProviderMeta:
        return self._meta[name]

    def begin(self, name: str) -> IOAuth2:
        return self._registry[name](self._meta[name])


reg = OAuthRegistry(
    base_redirect_url=oauth_settings.base_redirect_url,
    base_authorization_url=oauth_settings.base_authorization_url,
    base_revoke_url=oauth_settings.base_revoke_url,
)


@reg.provider("google", "Google", "fa-google", "#F44336")
def get_google(meta: ProviderMeta) -> IOAuth2:
    if not google_settings.oauth_allowed:
        raise ProviderNotAllowed()
    return GoogleOAuth(
        google_settings.client_id,
        google_settings.client_secret,
        meta.redirect_uri,
    )


@reg.provider("telegram", "Telegram", "fa-telegram", "#03A9F4")
def get_telegram(_meta: ProviderMeta) -> IOAuth2:
    if not telegram_settings.oauth_allowed:
        raise ProviderNotAllowed()
    return TelegramOAuth(
        telegram_settings.client_secret,
        f"{main_settings.api_url}/oauth/redirect/telegram",
    )


@reg.provider("yandex", "Yandex", "fa-yandex", "#EA4335")
def get_yandex(meta: ProviderMeta) -> IOAuth2:
    if not yandex_settings.oauth_allowed:
        raise ProviderNotAllowed()
    return YandexOAuth(
        yandex_settings.client_id,
        yandex_settings.client_secret,
        meta.redirect_uri,
    )
