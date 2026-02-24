from typing import Any

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from fastid.admin.auth import admin_auth
from fastid.admin.views.entities import NotificationAdmin, OAuthAccountAdmin, UserAdmin
from fastid.admin.views.settings import (
    AppAdmin,
    EmailTemplateAdmin,
    TelegramTemplateAdmin,
    WebhookAdmin,
    WebhookEventAdmin,
)
from fastid.admin.views.versioning import (
    AppVersionAdmin,
    EmailTemplateVersionAdmin,
    TelegramTemplateVersionAdmin,
    TransactionAdmin,
    UserVersionAdmin,
    WebhookVersionAdmin,
)
from fastid.core.base import AppFactory


class AdminAppFactory(AppFactory):
    name = "admin"

    def __init__(
        self,
        engine: Engine | AsyncEngine,
        **admin_kwargs: Any,
    ) -> None:
        self.engine = engine
        self.admin_kwargs = admin_kwargs

    def create(self) -> FastAPI:
        app = FastAPI()
        admin = Admin(
            app,
            self.engine,
            authentication_backend=admin_auth,
            **self.admin_kwargs,
        )
        # Users
        admin.add_view(UserAdmin)
        admin.add_view(OAuthAccountAdmin)
        admin.add_view(NotificationAdmin)
        # Settings
        admin.add_view(AppAdmin)
        admin.add_view(WebhookAdmin)
        admin.add_view(WebhookEventAdmin)
        admin.add_view(EmailTemplateAdmin)
        admin.add_view(TelegramTemplateAdmin)
        # Versioning
        admin.add_view(TransactionAdmin)
        admin.add_view(UserVersionAdmin)
        admin.add_view(AppVersionAdmin)
        admin.add_view(WebhookVersionAdmin)
        admin.add_view(EmailTemplateVersionAdmin)
        admin.add_view(TelegramTemplateVersionAdmin)
        return app
