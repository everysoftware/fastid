from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class MainSettings(BaseSettings):
    discovery_name: str = "fastapi"
    title: str = "FastAPI App"
    version: str = "0.1.0"
    env: Literal["dev", "prod"] = "dev"
    debug: bool = False

    base_url: HttpUrl = HttpUrl("http://localhost:8000")
    api_path: str = "/api/v1"

    @property
    def api_url(self) -> HttpUrl:
        return HttpUrl(f"{self.base_url}{self.api_path[1:]}")

    @property
    def oauth_login_url(self) -> HttpUrl:
        return HttpUrl(f"{self.api_url}/oauth/login")

    @property
    def oauth_callback_url(self) -> HttpUrl:
        return HttpUrl(f"{self.api_url}/oauth/callback")

    model_config = SettingsConfigDict(env_prefix="main_")


main_settings = MainSettings()
