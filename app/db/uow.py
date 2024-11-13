from __future__ import annotations

from typing import cast

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.base.uow import IUnitOfWork
from app.social.repositories import OAuthAccountRepository
from app.apps.repositories import AppRepository
from app.auth.repositories import UserRepository


class AlchemyUOW(IUnitOfWork):
    _session_factory: async_sessionmaker[AsyncSession]
    _session: AsyncSession

    users: UserRepository
    oauth_accounts: OAuthAccountRepository
    apps: AppRepository

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
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
