from app.main.config import main_settings
from app.oauth.config import (
    oauth_settings,
    google_settings,
    telegram_settings,
    yandex_settings,
)
from app.oauth.registry import OAuthRegistry
from app.oauth.schemas import ProviderMeta
from app.oauthlib.base import IOAuth2
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth

registry = OAuthRegistry(
    base_redirect_url=oauth_settings.base_redirect_url,
    base_authorization_url=oauth_settings.base_authorization_url,
    base_revoke_url=oauth_settings.base_revoke_url,
)


if google_settings.enabled:

    @registry.provider("google", "Google", "fa-google", "#F44336")
    def get_google(meta: ProviderMeta) -> IOAuth2:
        return GoogleOAuth(
            google_settings.client_id,
            google_settings.client_secret,
            meta.redirect_uri,
        )


if telegram_settings.enabled:

    @registry.provider("telegram", "Telegram", "fa-telegram", "#03A9F4")
    def get_telegram(_meta: ProviderMeta) -> IOAuth2:
        return TelegramOAuth(
            telegram_settings.bot_token,
            f"{main_settings.api_url}/oauth/redirect/telegram",
        )


if yandex_settings.enabled:

    @registry.provider("yandex", "Yandex", "fa-yandex", "#EA4335")
    def get_yandex(meta: ProviderMeta) -> IOAuth2:
        return YandexOAuth(
            yandex_settings.client_id,
            yandex_settings.client_secret,
            meta.redirect_uri,
        )
