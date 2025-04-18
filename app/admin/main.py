from typing import Any

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from app.admin.auth import admin_auth
from app.admin.views import OAuthAccountAdmin, OAuthClientAdmin, UserAdmin
from app.main.modules import Module


class AdminModule(Module):
    module_name = "admin"

    def __init__(
        self,
        engine: Engine | AsyncEngine,
        base_url: str = "/admin",
        **admin_kwargs: Any,
    ) -> None:
        self.engine = engine
        self.base_url = base_url
        self.admin_kwargs = admin_kwargs

    def install(self, app: FastAPI) -> None:
        admin_app = FastAPI()
        admin = Admin(
            admin_app,
            self.engine,
            base_url="/",
            authentication_backend=admin_auth,
            **self.admin_kwargs,
        )
        admin.add_view(UserAdmin)
        admin.add_view(OAuthClientAdmin)
        admin.add_view(OAuthAccountAdmin)
        app.mount(self.base_url, admin_app)
