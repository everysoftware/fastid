from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class AdminSettings(BaseSettings):
    enabled: bool = True
    favicon_url: HttpUrl = HttpUrl(
        "https://fastapi.tiangolo.com/img/favicon.png"
    )
    logo_url: HttpUrl = HttpUrl(
        "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    )

    model_config = SettingsConfigDict(env_prefix="admin_")


admin_settings = AdminSettings()
