import pytest

from app.auth.models import User
from app.db.uow import IUnitOfWork
from tests import mocks


@pytest.fixture
async def mock_user(uow: IUnitOfWork) -> User:
    user = User(**mocks.USER_RECORD)
    await uow.users.add(user)
    await uow.commit()

    return user
