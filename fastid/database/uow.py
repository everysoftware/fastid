from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Self

from sqlalchemy import select

from fastid.apps.repositories import AppRepository
from fastid.auth.repositories import UserRepository
from fastid.core.dependencies import log
from fastid.notify.repositories import EmailTemplateRepository, NotificationRepository, TelegramTemplateRepository
from fastid.oauth.repositories import OAuthAccountRepository, OAuthProviderRepository
from fastid.webhooks.repositories import WebhookEventRepository, WebhookRepository

if TYPE_CHECKING:
    from types import TracebackType

    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
    )


class SQLAlchemyUOW:
    users: UserRepository
    oauth_accounts: OAuthAccountRepository
    oauth_providers: OAuthProviderRepository
    apps: AppRepository
    email_templates: EmailTemplateRepository
    telegram_templates: TelegramTemplateRepository
    notifications: NotificationRepository
    webhooks: WebhookRepository
    webhook_events: WebhookEventRepository

    session_factory: async_sessionmaker[AsyncSession]
    session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self._active = False

    async def begin(self) -> None:
        if self._active:
            msg = "Unit of work is already active"
            raise RuntimeError(msg)
        self.session = self.session_factory()
        self._active = True
        self.users = UserRepository(self.session)
        self.oauth_accounts = OAuthAccountRepository(self.session)
        self.oauth_providers = OAuthProviderRepository(self.session)
        self.apps = AppRepository(self.session)
        self.email_templates = EmailTemplateRepository(self.session)
        self.telegram_templates = TelegramTemplateRepository(self.session)
        self.notifications = NotificationRepository(self.session)
        self.webhooks = WebhookRepository(self.session)
        self.webhook_events = WebhookEventRepository(self.session)

    @property
    def is_active(self) -> bool:
        return self._active

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        task = asyncio.create_task(self.session.close())
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await task
            raise
        finally:
            self._active = False

    async def flush(self) -> None:
        await self.session.flush()

    async def healthcheck(self) -> None:
        await self.session.execute(select(1))

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> bool:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        except BaseException:
            try:
                await self.close()
            except Exception:  # noqa: BLE001 - preserve the original transaction failure
                log.exception("Session cleanup failed after transaction failure")
            raise
        else:
            await self.close()
        return False
