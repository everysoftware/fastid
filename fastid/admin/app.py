from fastid.admin.config import admin_settings
from fastid.admin.factory import AdminAppFactory
from fastid.core.config import main_settings
from fastid.database.dependencies import engine

admin_app = AdminAppFactory(
    engine,
    title=f"{main_settings.title} Admin",
    favicon_url=admin_settings.favicon_url,
    logo_url=admin_settings.logo_url,
).create()
