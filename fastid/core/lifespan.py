from collections.abc import Callable
from types import TracebackType
from typing import Self

from fastid.admin.config import admin_settings
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.cache.exceptions import LockError
from fastid.cache.storage import CacheStorage
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.notify.repositories import EmailTemplateSlugSpecification, TelegramTemplateSlugSpecification
from fastid.notify.utils import collect_email_templates, collect_telegram_templates
from fastid.oauth.models import OAUTH_PROVIDER_NAMES, OAuthProvider
from fastid.oauth.repositories import OAuthProviderNameSpecification
from fastid.webhooks.senders.dependencies import client as webhooks_client


class LifespanTasks:
    def __init__(self, *, uow_factory: Callable[[], SQLAlchemyUOW], cache_factory: Callable[[], CacheStorage]) -> None:
        self.uow = uow_factory()
        self.cache = cache_factory()

    async def on_startup(self) -> None:
        await self.healthcheck()
        try:
            async with self.cache.lock("seed", blocking=True):
                await self.create_admin()
                await self.create_templates()
                await self.create_oauth_providers()
        except LockError:
            pass

    async def healthcheck(self) -> None:
        await self.uow.healthcheck()
        await self.cache.healthcheck()

    async def create_admin(self) -> None:
        try:
            await self.uow.users.find(EmailUserSpecification(admin_settings.email))
        except NoResultFoundError:
            admin = User(first_name="Admin", last_name="User", email=admin_settings.email)
            admin.set_password(admin_settings.password)
            admin.verify()
            admin.grant_superuser()
            await self.uow.users.add(admin)

    async def create_templates(self) -> None:
        for email_t in collect_email_templates():
            try:
                await self.uow.email_templates.find(EmailTemplateSlugSpecification(email_t.slug))
            except NoResultFoundError:
                await self.uow.email_templates.add(email_t)

        for telegram_t in collect_telegram_templates():
            try:
                await self.uow.telegram_templates.find(TelegramTemplateSlugSpecification(telegram_t.slug))
            except NoResultFoundError:
                await self.uow.telegram_templates.add(telegram_t)

    async def create_oauth_providers(self) -> None:
        for name in OAUTH_PROVIDER_NAMES:
            try:
                await self.uow.oauth_providers.find(OAuthProviderNameSpecification(name))
            except NoResultFoundError:
                await self.uow.oauth_providers.add(
                    OAuthProvider(name=name, enabled=False, client_id="", client_secret=""),
                )

    async def on_shutdown(self) -> None:
        await self.cache.client.aclose()
        await webhooks_client.aclose()

    async def __aenter__(self) -> Self:
        await self.uow.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        await self.uow.__aexit__(exc_type, exc_val, exc_tb)
        return False
