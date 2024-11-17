from typing import Sequence

from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class AppsSettings(BaseSettings):
    default_name: str = "YourApp"
    default_slug: str = "your-app"
    default_redirect_uris: Sequence[str] = (
        "https://yourapp.com/auth/callback",
    )

    model_config = SettingsConfigDict(env_prefix="apps_")


apps_settings = AppsSettings()
