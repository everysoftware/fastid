from faker import Faker

faker = Faker()

USER_CREATE = {
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "email": faker.email(),
}


class MockError(Exception):
    pass
