from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class AppsSettings(BaseSettings):
    default_name: str = "Frontend"
    default_id: str = "frontend"
    default_secret: str = "changethis"
    default_primary_url: str = "http://localhost:8000"
    default_redirect_uris: list[str] = ["http://localhost:8000"]

    model_config = SettingsConfigDict(env_prefix="apps_")


apps_settings = AppsSettings()
