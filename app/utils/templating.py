from fastapi.templating import Jinja2Templates

from app.runner.config import settings

FRONTEND_URL = settings.oauth.primary_url

templates = Jinja2Templates(directory="templates/pages")

templates.env.globals["app_display_name"] = settings.app_display_name
templates.env.globals["google_login_url"] = (
    f"{FRONTEND_URL}/oauth/google/login"
)
templates.env.globals["yandex_login_url"] = (
    f"{FRONTEND_URL}/oauth/yandex/login"
)
templates.env.globals["telegram_login_url"] = (
    f"{FRONTEND_URL}/oauth/telegram/login"
)
