from typing import Self, Any

from app.apps.config import apps_settings
from app.apps.models import App
from app.apps.repositories import IsAppExists
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.config import auth_settings
from app.cache.dependencies import redis_client
from app.db.connection import session_factory
from app.db.uow import AlchemyUOW


class Background:
    def __init__(self) -> None:
        self.uow = AlchemyUOW(session_factory)
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
            IsActiveUser(auth_settings.admin_email)
        )
        if not user:
            user = User(
                first_name="Admin",
                email=auth_settings.admin_email,
            )
            user.set_password(auth_settings.admin_password)
            user.verify()
            user.grant_superuser()
            await self.uow.users.add(user)

        # Register first user
        user = await self.uow.users.find(
            IsActiveUser(auth_settings.default_user_email)
        )
        if not user:
            user = User(
                first_name="First User",
                email=auth_settings.default_user_email,
            )
            user.set_password(auth_settings.default_user_password)
            user.verify()
            await self.uow.users.add(user)

    async def register_apps(self) -> None:
        client = await self.uow.apps.find(
            IsAppExists(apps_settings.default_id)
        )
        if not client:
            app = App(
                name=apps_settings.default_name,
                client_id=apps_settings.default_id,
                client_secret=apps_settings.default_secret,
                redirect_uris=";".join(apps_settings.default_redirect_uris),
            )
            await self.uow.apps.add(app)
