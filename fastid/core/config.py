from enum import auto
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseEnum, BaseSettings
from fastid.core.urls import join_url_path


class Environment(BaseEnum):
    local = auto()
    test = auto()
    dev = auto()
    prod = auto()


class CoreSettings(BaseSettings):
    env: Environment = Environment.prod
    debug: bool = False
    behind_proxy: bool = True
    public_url: str | None = None

    api_path: str = "/api/v1"
    admin_path: str = "/admin"
    frontend_path: str = ""

    @field_validator("public_url")
    @classmethod
    def validate_public_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            msg = "public_url must be an absolute HTTP(S) URL"
            raise ValueError(msg)
        if parsed.query or parsed.fragment:
            msg = "public_url must not contain a query or fragment"
            raise ValueError(msg)
        return value.rstrip("/")


core_settings = CoreSettings()


class BrandingSettings(BaseSettings):
    title: str = "FastID"
    service_name: str = "fastid"
    api_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} API")
    frontend_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} Frontend")
    admin_swagger_title: str = Field(default_factory=lambda data: f"{data['title']} Admin")
    admin_favicon_url: str = join_url_path(core_settings.frontend_path, "static/assets/favicon.png")
    admin_logo_url: str = join_url_path(core_settings.frontend_path, "static/assets/logo_text.png")
    notify_from: str = Field(default_factory=lambda data: data["title"])

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}branding_")


branding_settings = BrandingSettings()
