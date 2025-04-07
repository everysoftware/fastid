from faker import Faker

faker = Faker()

USER_CREATE = {
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "email": faker.email(),
}

CACHE_RECORD = {
    "key": faker.word(),
    "value": faker.word(),
}


class MockError(Exception):
    pass
