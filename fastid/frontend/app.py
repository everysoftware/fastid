from fastid.core.config import main_settings
from fastid.frontend.factory import FrontendAppFactory

frontend_app = FrontendAppFactory(title=main_settings.title).create()
