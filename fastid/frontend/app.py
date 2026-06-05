from fastid.core.config import branding_settings
from fastid.frontend.factory import FrontendAppFactory

frontend_app = FrontendAppFactory(title=branding_settings.frontend_swagger_title).create()
