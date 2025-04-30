from faker import Faker

from fastid.apps.schemas import AppCreate, AppUpdate
from fastid.auth.schemas import UserCreate, UserUpdate
from fastid.security.crypto import crypt_ctx
from tests.utils.auth import generate_random_state

faker = Faker()

USER_CREATE = UserCreate(
    first_name=faker.first_name(),
    last_name=faker.last_name(),
    email=faker.email(),
    password=faker.password(),
)
USER_UPDATE = UserUpdate(first_name=faker.first_name(), last_name=faker.last_name())

USER_SU_CREATE = UserCreate(
    first_name=faker.first_name(),
    last_name=faker.last_name(),
    email=faker.email(),
    password=faker.password(),
)

USER_RECORD = {
    "first_name": USER_CREATE.first_name,
    "last_name": USER_CREATE.last_name,
    "email": USER_CREATE.email,
    "hashed_password": crypt_ctx.hash(USER_CREATE.password),
}

USER_SU_RECORD = {
    "first_name": USER_SU_CREATE.first_name,
    "last_name": USER_SU_CREATE.last_name,
    "email": USER_SU_CREATE.email,
    "hashed_password": crypt_ctx.hash(USER_SU_CREATE.password),
    "is_superuser": True,
}

CACHE_RECORD = {
    "key": faker.word(),
    "value": faker.word(),
}

APP_CREATE = AppCreate(name="Test App", slug="test-app", redirect_uris="https://google.com")
APP_UPDATE = AppUpdate(name="New Test App")
STATE = generate_random_state()


class MockError(Exception):
    pass
