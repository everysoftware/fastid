from __future__ import annotations

import abc
from abc import ABC
from typing import TYPE_CHECKING, Any, Self, cast

from app.apps.repositories import AppRepository
from app.auth.repositories import UserRepository
from app.oauth.repositories import OAuthAccountRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
    )


class IUnitOfWork(ABC):
    users: UserRepository
    oauth_accounts: OAuthAccountRepository
    apps: AppRepository

    @abc.abstractmethod
    async def begin(self) -> None: ...

    @property
    @abc.abstractmethod
    def is_active(self) -> bool: ...

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...

    @abc.abstractmethod
    async def close(self) -> None: ...

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()


class SQLAlchemyUOW(IUnitOfWork):
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
        if not self._session:
            return False
        return cast(bool, self._session.is_active)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()
