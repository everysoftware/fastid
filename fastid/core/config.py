from enum import auto

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseEnum, BaseSettings


class Environment(BaseEnum):
    local = auto()
    test = auto()
    dev = auto()
    prod = auto()


class CoreSettings(BaseSettings):
    env: Environment = Environment.local
    debug: bool = False

    base_url: str = "http://localhost:8012"
    api_path: str = "/api/v1"
    admin_path: str = "/admin"
    frontend_path: str = ""

    @property
    def api_url(self) -> str:
        return f"{self.base_url}/{self.api_path[1:]}"

    @property
    def frontend_url(self) -> str:
        if self.frontend_path == "":
            return self.base_url
        return f"{self.base_url}/{self.frontend_path[1:]}"


core_settings = CoreSettings()


class BrandingSettings(BaseSettings):
    title: str = "FastID"
    service_name: str = "fastid"
    api_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} API")
    frontend_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} Frontend")
    admin_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} Admin")
    admin_favicon_url: str = f"{core_settings.frontend_url}/static/assets/favicon.png"
    admin_logo_url: str = f"{core_settings.frontend_url}/static/assets/logo_text.png"
    notify_from: str = Field(default_factory=lambda data: data["title"])

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}branding_")


branding_settings = BrandingSettings()
