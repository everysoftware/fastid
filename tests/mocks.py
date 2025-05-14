from typing import Any

from faker import Faker
from fastlink.schemas import OAuth2Callback, OpenID, OpenIDBearer, TokenResponse
from fastlink.telegram.schemas import TelegramCallback
from fastlink.telegram.utils import compute_hmac_sha256

from fastid.apps.schemas import AppCreate, AppUpdate
from fastid.auth.schemas import UserCreate, UserUpdate
from fastid.oauth.config import telegram_settings
from fastid.security.crypto import crypt_ctx
from tests.utils.auth import generate_random_state

faker = Faker()


def user_create_factory() -> UserCreate:
    return UserCreate(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        password=faker.password(),
    )


def user_record_factory(base: UserCreate, **kwargs: Any) -> dict[str, Any]:
    return {
        "first_name": base.first_name,
        "last_name": base.last_name,
        "email": base.email,
        "hashed_password": crypt_ctx.hash(base.password),
        **kwargs,
    }


USER_CREATE = user_create_factory()
USER_UPDATE = UserUpdate(first_name=faker.first_name(), last_name=faker.last_name())

USER_SU_CREATE = user_create_factory()
USER_TG_CREATE = user_create_factory()

USER_RECORD = user_record_factory(USER_CREATE)
USER_SU_RECORD = user_record_factory(USER_SU_CREATE, is_superuser=True)
USER_TG_RECORD = user_record_factory(USER_TG_CREATE, telegram_id=faker.random_number())

CACHE_RECORD = {
    "key": faker.word(),
    "value": faker.word(),
}

APP_CREATE = AppCreate(name="Test App", slug="test-app", redirect_uris="https://google.com")
APP_UPDATE = AppUpdate(name="New Test App")

OAUTH_STATE = generate_random_state()
OAUTH_CALLBACK = OAuth2Callback(code=faker.pystr(min_chars=8, max_chars=256), state=OAUTH_STATE)
TELEGRAM_CALLBACK_PAYLOAD = {
    "id": faker.random_number(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "username": faker.user_name(),
    "picture": faker.image_url(),
    "auth_date": int(faker.date_time().timestamp()),
}
TELEGRAM_CALLBACK_PAYLOAD["hash"] = compute_hmac_sha256(TELEGRAM_CALLBACK_PAYLOAD, telegram_settings.bot_token)
TELEGRAM_CALLBACK = TelegramCallback(**TELEGRAM_CALLBACK_PAYLOAD)
OAUTH_TOKEN_RESPONSE = TokenResponse(
    access_token=faker.pystr(min_chars=8, max_chars=256),
    expires_in=3600,
    refresh_token=faker.pystr(min_chars=8, max_chars=256),
    scope="openid email profile",
)


def openid_factory(provider: str, **kwargs: Any) -> OpenID:
    return OpenID(
        id=str(faker.random_number(digits=10)),
        provider=provider,
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        picture=faker.image_url(),
        **kwargs,
    )


GOOGLE_OPENID = openid_factory("google")
YANDEX_OPENID = openid_factory("yandex")
TELEGRAM_OPENID = openid_factory("telegram")
TELEGRAM_OPENID.email = None

GOOGLE_OPENID_BEARER = OpenIDBearer(**GOOGLE_OPENID.model_dump(), **OAUTH_TOKEN_RESPONSE.model_dump())
YANDEX_OPENID_BEARER = OpenIDBearer(**YANDEX_OPENID.model_dump(), **OAUTH_TOKEN_RESPONSE.model_dump())
TELEGRAM_OPENID_BEARER = OpenIDBearer(**TELEGRAM_OPENID.model_dump(), **OAUTH_TOKEN_RESPONSE.model_dump())


class MockError(Exception):
    pass
