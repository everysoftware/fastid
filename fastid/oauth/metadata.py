from fastid.core.config import core_settings
from fastid.core.urls import join_url_path
from fastid.integrations.config import (
    integration_settings,
)
from fastid.oauth.schemas import UIProviderMeta, UIProviderMetaEntry

UI_META = UIProviderMeta()

BASE_OAUTH_URL = join_url_path(core_settings.api_path, "oauth")
BASE_AUTHORIZATION_URL = f"{BASE_OAUTH_URL}/login"
BASE_REVOKE_URL = f"{BASE_OAUTH_URL}/revoke"

UI_META.providers["google"] = UIProviderMetaEntry(
    name="google",
    title="Google",
    icon="fa-google",
    color="#F44336",
    authorization_url=f"{BASE_AUTHORIZATION_URL}/google",
    revoke_url=f"{BASE_REVOKE_URL}/google",
    enabled=integration_settings.google_oauth_enabled,
)
UI_META.providers["telegram"] = UIProviderMetaEntry(
    name="telegram",
    title="Telegram",
    icon="fa-telegram",
    color="#03A9F4",
    authorization_url=f"{BASE_AUTHORIZATION_URL}/telegram",
    revoke_url=f"{BASE_REVOKE_URL}/telegram",
    enabled=integration_settings.telegram_widget_enabled,
)
UI_META.providers["yandex"] = UIProviderMetaEntry(
    name="yandex",
    title="Yandex",
    icon="fa-yandex",
    color="#EA4335",
    authorization_url=f"{BASE_AUTHORIZATION_URL}/yandex",
    revoke_url=f"{BASE_REVOKE_URL}/yandex",
    enabled=integration_settings.yandex_oauth_enabled,
)
UI_META.providers["vk"] = UIProviderMetaEntry(
    name="vk",
    title="VK",
    icon="fa-vk",
    color="#0077FF",
    authorization_url=f"{BASE_AUTHORIZATION_URL}/vk",
    revoke_url=f"{BASE_REVOKE_URL}/vk",
    enabled=integration_settings.vk_oauth_enabled,
)
