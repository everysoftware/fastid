from typing import Any

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from app.admin.auth import admin_auth
from app.admin.views import OAuthAccountAdmin, UserAdmin, OAuthClientAdmin
from app.plugins.base import Plugin


class AdminPlugin(Plugin):
    plugin_name = "admin"

    def __init__(
        self, engine: Engine | AsyncEngine, **admin_kwargs: Any
    ) -> None:
        self.engine = engine
        self.admin_kwargs = admin_kwargs

    def install(self, app: FastAPI) -> None:
        admin = Admin(
            app,
            self.engine,
            authentication_backend=admin_auth,
            **self.admin_kwargs,
        )

        admin.add_view(UserAdmin)
        admin.add_view(OAuthClientAdmin)
        admin.add_view(OAuthAccountAdmin)
