import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.auth.models import User
from app.db.exceptions import NoResultFoundError
from app.db.uow import IUnitOfWork, SQLAlchemyUOW
from tests import mocks
from tests.mocks import MockError


async def test_uow_auto_commit(uow: IUnitOfWork, engine: AsyncEngine) -> None:
    async with uow:
        test_user = User(**mocks.USER_RECORD)
        await uow.users.add(test_user)

    async with uow:
        user = await uow.users.get(test_user.id)
        assert user.id == test_user.id


async def test_uow_auto_rollback(uow: IUnitOfWork, engine: AsyncEngine) -> None:
    with pytest.raises(MockError):  # noqa: PT012
        async with uow:
            test_user = User(**mocks.USER_RECORD)
            await uow.users.add(test_user)
            await uow.flush()
            raise MockError

    async with uow:
        with pytest.raises(NoResultFoundError):
            await uow.users.get(test_user.id)


async def test_uow_is_active(session_factory: async_sessionmaker[AsyncSession]) -> None:
    uow = SQLAlchemyUOW(session_factory)
    assert not uow.is_active
    async with uow:
        assert uow.is_active
