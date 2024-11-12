from typing import Self, Any

from app.apps.repositories import IsAppExists
from app.apps.schemas import App
from app.auth.repositories import IsActiveUser
from app.auth.schemas import User
from app.cache.dependencies import redis_client
from app.db.connection import async_session_factory
from app.db.uow import AlchemyUOW
from app.runner.config import settings


class Background:
    def __init__(self) -> None:
        self.uow = AlchemyUOW(async_session_factory)
        self.redis = redis_client

    async def __aenter__(self) -> Self:
        await self.uow.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: type[Exception], exc_val: Exception, exc_tb: Any
    ) -> None:
        await self.uow.__aexit__(exc_type, exc_val, exc_tb)

    async def healthcheck(self) -> None:
        await self.redis.ping()

    async def register_users(self) -> None:
        # Register admin
        user = await self.uow.users.find(
            IsActiveUser(settings.auth.admin_email)
        )
        if not user:
            user = User(
                first_name="Admin",
                email=settings.auth.admin_email,
                password=settings.auth.admin_password,
            )
            user.hash_password()
            user.verify()
            user.grant_superuser()
            await self.uow.users.add(user)

        # Register first user
        user = await self.uow.users.find(
            IsActiveUser(settings.auth.first_user_email)
        )
        if not user:
            user = User(
                first_name="First User",
                email=settings.auth.first_user_email,
                password=settings.auth.first_user_password,
            )
            user.hash_password()
            user.verify()
            await self.uow.users.add(user)

    async def register_apps(self) -> None:
        client = await self.uow.apps.find(IsAppExists(settings.oauth.id))
        if client:
            app = App(
                name=settings.oauth.name,
                client_id=settings.oauth.id,
                client_secret=settings.oauth.secret,
                redirect_uris=";".join(settings.oauth.redirect_uris),
            )
            await self.uow.apps.add(app)
