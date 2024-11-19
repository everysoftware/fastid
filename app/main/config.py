from typing import Literal

from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class MainSettings(BaseSettings):
    discovery_name: str = "fastapi"
    title: str = "FastAPI App"
    version: str = "0.1.0"
    env: Literal["dev", "prod"] = "dev"
    debug: bool = False

    base_url: str = "http://localhost:8000"
    api_path: str = "/api/v1"

    @property
    def api_url(self) -> str:
        return f"{self.base_url}/{self.api_path[1:]}"

    model_config = SettingsConfigDict(env_prefix="main_")


main_settings = MainSettings()
