from pydantic_settings import SettingsConfigDict

from fastid.core.config import main_settings
from fastid.core.schemas import BaseSettings


class AdminSettings(BaseSettings):
    enabled: bool = True
    email: str = "admin@fastid.com"
    username: str = "admin"
    password: str = "admin"
    favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png"
    logo_url: str = "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"

    model_config = SettingsConfigDict(env_prefix="admin_")


favicon_url = f"{main_settings.base_url}/static/assets/favicon.png"
logo_url = f"{main_settings.base_url}/static/assets/logo_text.png"
admin_settings = AdminSettings(favicon_url=favicon_url, logo_url=logo_url)
