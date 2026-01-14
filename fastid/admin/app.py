from typing import Any

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from fastid.admin.auth import admin_auth
from fastid.admin.views import (
    EmailTemplateAdmin,
    NotificationAdmin,
    OAuthAccountAdmin,
    OAuthClientAdmin,
    TelegramTemplateAdmin,
    UserAdmin,
)
from fastid.core.base import MiniApp


class AdminMiniApp(MiniApp):
    name = "admin"

    def __init__(
        self,
        engine: Engine | AsyncEngine,
        base_url: str = "/admin",
        **admin_kwargs: Any,
    ) -> None:
        self.engine = engine
        self.base_url = base_url
        self.admin_kwargs = admin_kwargs

    def create(self) -> FastAPI:
        app = FastAPI()
        admin = Admin(
            app,
            self.engine,
            base_url="/",
            authentication_backend=admin_auth,
            **self.admin_kwargs,
        )
        admin.add_view(UserAdmin)
        admin.add_view(OAuthClientAdmin)
        admin.add_view(OAuthAccountAdmin)
        admin.add_view(EmailTemplateAdmin)
        admin.add_view(TelegramTemplateAdmin)
        admin.add_view(NotificationAdmin)
        return app

    def install(self, app: FastAPI) -> None:
        admin_app = self.create()
        app.mount(self.base_url, admin_app)
        app.extra["admin_app"] = admin_app
