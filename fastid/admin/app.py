from fastid.admin.factory import AdminAppFactory
from fastid.core.config import branding_settings
from fastid.database.dependencies import engine

admin_app = AdminAppFactory(
    engine,
    title=branding_settings.admin_swagger_title,
    favicon_url=branding_settings.admin_favicon_url,
    logo_url=branding_settings.admin_logo_url,
    base_url="",
).create()
