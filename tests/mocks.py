from typing import Any

from faker import Faker

from fastid.apps.schemas import AppCreate, AppUpdate
from fastid.auth.schemas import UserCreate, UserUpdate
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
STATE = generate_random_state()


class MockError(Exception):
    pass
