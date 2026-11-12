import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from fastid.auth.models import User
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from tests import mocks
from tests.mocks import MockError


async def test_uow_auto_commit(uow: SQLAlchemyUOW, engine: AsyncEngine) -> None:
    async with SQLAlchemyUOW(uow.session_factory) as transaction:
        test_user = User(**mocks.USER_RECORD)
        await transaction.users.add(test_user)

    async with SQLAlchemyUOW(uow.session_factory) as transaction:
        user = await transaction.users.get(test_user.id)
        assert user.id == test_user.id


async def test_uow_auto_rollback(uow: SQLAlchemyUOW, engine: AsyncEngine) -> None:
    with pytest.raises(MockError):  # noqa: PT012
        async with SQLAlchemyUOW(uow.session_factory) as transaction:
            test_user = User(**mocks.USER_RECORD)
            await transaction.users.add(test_user)
            await transaction.flush()
            raise MockError

    async with SQLAlchemyUOW(uow.session_factory) as transaction:
        with pytest.raises(NoResultFoundError):
            await transaction.users.get(test_user.id)


async def test_uow_is_active(session_factory: async_sessionmaker[AsyncSession]) -> None:
    uow = SQLAlchemyUOW(session_factory)
    assert not uow.is_active
    async with uow:
        assert uow.is_active


async def test_uow_hc(uow: SQLAlchemyUOW) -> None:
    await uow.healthcheck()
