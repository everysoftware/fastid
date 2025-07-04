from typing import Any

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from fastid.core.base import MiniApp
from fastid.dashboard.auth import admin_auth
from fastid.dashboard.views import OAuthAccountAdmin, OAuthClientAdmin, UserAdmin


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
        return app

    def install(self, app: FastAPI) -> None:
        admin_app = self.create()
        app.mount(self.base_url, admin_app)
        app.extra["admin_app"] = admin_app
