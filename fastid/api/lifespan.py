from typing import Any, Self

from fastid.admin.config import admin_settings
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.cache.dependencies import redis_client
from fastid.database.dependencies import session_factory
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.notify.repositories import EmailTemplateSlugSpecification, TelegramTemplateSlugSpecification
from fastid.notify.utils import EMAIL_TEMPLATES, TELEGRAM_TEMPLATES


class LifespanTasks:
    def __init__(self) -> None:
        self.uow = SQLAlchemyUOW(session_factory)
        self.redis = redis_client

    async def on_startup(self) -> None:
        await self.healthcheck()

        try:
            await self.uow.users.find(EmailUserSpecification(admin_settings.email))
        except NoResultFoundError:
            admin = User(first_name="Admin", last_name="User", email=admin_settings.email)
            admin.set_password(admin_settings.password)
            admin.verify()
            admin.grant_superuser()
            await self.uow.users.add(admin)

        for email_t in EMAIL_TEMPLATES:
            try:
                await self.uow.email_templates.find(EmailTemplateSlugSpecification(email_t.slug))
            except NoResultFoundError:
                await self.uow.email_templates.add(email_t)

        for telegram_t in TELEGRAM_TEMPLATES:
            try:
                await self.uow.telegram_templates.find(TelegramTemplateSlugSpecification(telegram_t.slug))
            except NoResultFoundError:
                await self.uow.telegram_templates.add(telegram_t)

    async def on_shutdown(self) -> None:
        await self.redis.aclose()

    async def healthcheck(self) -> None:
        await self.redis.ping()

    async def __aenter__(self) -> Self:
        await self.uow.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        await self.uow.__aexit__(exc_type, exc_val, exc_tb)
        return False
