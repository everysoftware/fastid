from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import admin_auth
from app.admin.views import OAuthAccountAdmin, UserAdmin, OAuthClientAdmin
from app.runner.config import settings
from app.db.connection import async_engine

app = FastAPI()
admin = Admin(
    app,
    async_engine,
    authentication_backend=admin_auth,
    base_url="/",
    favicon_url="/static/assets/favicon.ico",
    title=f"Admin | {settings.app_display_name}",
)

admin.add_view(UserAdmin)
admin.add_view(OAuthClientAdmin)
admin.add_view(OAuthAccountAdmin)
