from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class APISettings(BaseSettings):
    discovery_name: str = "fastapi"
    title: str = "FastAPI App"
    version: str = "0.1.0"
    root_path: str = "/api/v1"
    env: Literal["dev", "prod"] = "dev"
    debug: bool = False
    domain: HttpUrl = HttpUrl("http://localhost:8000")

    @property
    def v1_url(self) -> HttpUrl:
        return HttpUrl(f"{self.domain}{self.root_path[1:]}")

    @property
    def oauth_callback_url(self) -> HttpUrl:
        return HttpUrl(f"{self.v1_url}/oauth/callback")

    model_config = SettingsConfigDict(env_prefix="api_")


api_settings = APISettings()
