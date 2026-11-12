import asyncio
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fastid.database.uow import SQLAlchemyUOW


@pytest.mark.parametrize("operation", ["commit", "rollback"])
async def test_cleanup_after_transaction_failure(
    operation: str, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    uow = SQLAlchemyUOW(session_factory)
    await uow.begin()
    session = uow.session
    failure = RuntimeError("transaction failed")
    setattr(session, operation, AsyncMock(side_effect=failure))
    closed = False
    original_close = session.close

    async def close() -> None:
        nonlocal closed
        await original_close()
        closed = True

    session.close = close
    with pytest.raises(RuntimeError, match="transaction failed"):
        await uow.__aexit__(None if operation == "commit" else ValueError, None, None)
    assert closed
    assert not uow.is_active


async def test_reentry_keeps_original_session(session_factory: async_sessionmaker[AsyncSession]) -> None:
    uow = SQLAlchemyUOW(session_factory)
    async with uow:
        original = uow.session
        with pytest.raises(RuntimeError, match="active"):
            await uow.begin()
        assert uow.session is original
    assert not uow.is_active


async def test_cleanup_after_cancellation(session_factory: async_sessionmaker[AsyncSession]) -> None:
    uow = SQLAlchemyUOW(session_factory)
    with pytest.raises(asyncio.CancelledError):
        async with uow:
            raise asyncio.CancelledError
    assert not uow.is_active
