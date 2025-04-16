from faker import Faker

from app.auth.backend import crypt_ctx
from app.auth.schemas import UserCreate

faker = Faker()

USER_CREATE = UserCreate(
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
CACHE_RECORD = {
    "key": faker.word(),
    "value": faker.word(),
}


class MockError(Exception):
    pass
