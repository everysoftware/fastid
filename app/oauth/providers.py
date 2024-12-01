from app.main.config import main_settings
from app.oauth.config import (
    oauth_settings,
    google_settings,
    telegram_settings,
    yandex_settings,
)
from app.oauthlib.registry import ProviderRegistry
from app.oauthlib.base import OAuth2Flow
from app.oauthlib.google import GoogleOAuth
from app.oauthlib.telegram import TelegramOAuth
from app.oauthlib.yandex import YandexOAuth

google_oauth = GoogleOAuth(
    google_settings.client_id,
    google_settings.client_secret,
    f"{oauth_settings.base_redirect_url}/telegram",
)
yandex_oauth = YandexOAuth(
    yandex_settings.client_id,
    yandex_settings.client_secret,
    f"{oauth_settings.base_redirect_url}/yandex",
)
telegram_oauth = TelegramOAuth(
    telegram_settings.bot_token,
    redirect_uri=f"{main_settings.api_url}/oauth/redirect/telegram",
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
