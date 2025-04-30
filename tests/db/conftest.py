import pytest

from fastid.auth.models import User
from fastid.database.uow import SQLAlchemyUOW
from tests import mocks


@pytest.fixture
async def mock_user(uow: SQLAlchemyUOW) -> User:
    user = User(**mocks.USER_RECORD)
    await uow.users.add(user)
    await uow.commit()

    return user
