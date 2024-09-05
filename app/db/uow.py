from __future__ import annotations

from typing import Any, cast, Self

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    AsyncSessionTransaction,
)

from app.sso.repositories import OIDCAccountRepository
from app.users.repositories import UserRepository


class UOW:
    factory: async_sessionmaker[AsyncSession]
    session: AsyncSession
    transaction: AsyncSessionTransaction

    users: UserRepository
    oidc_accounts: OIDCAccountRepository

    def __init__(self, factory: async_sessionmaker[AsyncSession]):
        self.factory = factory

    @property
    def is_opened(self) -> bool:
        if not self.session:
            return False
        return cast(bool, self.session.is_active)

    async def on_open(self) -> None:
        self.users = UserRepository(self.session)
        self.oidc_accounts = OIDCAccountRepository(self.session)

    async def open(self) -> None:
        self.session = self.factory()
        await self.session.__aenter__()
        self.transaction = self.session.begin()
        await self.transaction.__aenter__()
        await self.on_open()

    async def close(self, type_: Any, value: Any, traceback: Any) -> None:
        await self.transaction.__aexit__(type_, value, traceback)
        await self.session.__aexit__(type_, value, traceback)

    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, type_: Any, value: Any, traceback: Any) -> None:
        await self.close(type_, value, traceback)
