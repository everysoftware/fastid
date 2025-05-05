from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Self, cast

from fastid.apps.repositories import AppRepository
from fastid.auth.repositories import UserRepository
from fastid.oauth.repositories import OAuthAccountRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
    )


class SQLAlchemyUOW:
    users: UserRepository
    oauth_accounts: OAuthAccountRepository
    apps: AppRepository

    _session_factory: async_sessionmaker[AsyncSession]
    _session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def begin(self) -> None:
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.oauth_accounts = OAuthAccountRepository(self._session)
        self.apps = AppRepository(self._session)

    @property
    def is_active(self) -> bool:
        if not hasattr(self, "_session") or not self._session:
            return False
        return cast(bool, self._session.is_active)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        task = asyncio.create_task(self._session.close())
        await asyncio.shield(task)

    async def flush(self) -> None:
        await self._session.flush()

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()
        return False
