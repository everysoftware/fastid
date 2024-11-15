from fastapi.templating import Jinja2Templates

from app.main.config import api_settings
from app.apps.config import apps_settings

FRONTEND_URL = apps_settings.default_primary_url

templates = Jinja2Templates(directory="templates/pages")

templates.env.globals["app_title"] = api_settings.title
templates.env.globals["google_login_url"] = (
    f"{FRONTEND_URL}/oauth/google/login"
)
templates.env.globals["yandex_login_url"] = (
    f"{FRONTEND_URL}/oauth/yandex/login"
)
templates.env.globals["telegram_login_url"] = (
    f"{FRONTEND_URL}/oauth/telegram/login"
)
