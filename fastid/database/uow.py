from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Self, cast

from sqlalchemy import select

from fastid.apps.repositories import AppRepository
from fastid.auth.repositories import UserRepository
from fastid.notify.repositories import EmailTemplateRepository, TelegramTemplateRepository
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
    email_templates: EmailTemplateRepository
    telegram_templates: TelegramTemplateRepository

    session_factory: async_sessionmaker[AsyncSession]
    session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def begin(self) -> None:
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.oauth_accounts = OAuthAccountRepository(self.session)
        self.apps = AppRepository(self.session)
        self.email_templates = EmailTemplateRepository(self.session)
        self.telegram_templates = TelegramTemplateRepository(self.session)

    @property
    def is_active(self) -> bool:
        if not hasattr(self, "session") or not self.session:
            return False
        return cast(bool, self.session.is_active)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        task = asyncio.create_task(self.session.close())
        await asyncio.shield(task)

    async def flush(self) -> None:
        await self.session.flush()

    async def healthcheck(self) -> None:
        await self.session.execute(select(1))

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
