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
    def authorization_endpoint(self) -> str:
        return f"{self.base_url}/authorize"

    @property
    def api_url(self) -> str:
        return f"{self.base_url}/{self.api_path[1:]}"

    @property
    def token_endpoint(self) -> str:
        return f"{self.api_url}/token"

    @property
    def userinfo_endpoint(self) -> str:
        return f"{self.api_url}/userinfo"

    @property
    def oauth_login_url(self) -> str:
        return f"{self.api_url}/oauth/login"

    @property
    def oauth_callback_url(self) -> str:
        return f"{self.api_url}/oauth/callback"

    model_config = SettingsConfigDict(env_prefix="main_")


main_settings = MainSettings()
