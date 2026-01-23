from collections.abc import Sequence
from enum import StrEnum, auto

from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import BaseSettings


class Environment(StrEnum):
    local = auto()
    test = auto()
    dev = auto()
    prod = auto()


class MainSettings(BaseSettings):
    discovery_name: str = "fastid"
    title: str = "FastID"
    version: str = "0.1.0"
    env: Environment = Environment.local
    debug: bool = False

    base_url: str = "http://localhost:8012"
    api_path: str = "/api/v1"

    @property
    def api_url(self) -> str:
        return f"{self.base_url}/{self.api_path[1:]}"

    model_config = SettingsConfigDict(env_prefix="main_")


class CORSSettings(BaseSettings):
    origins: Sequence[str] = ("*",)
    origin_regex: str | None = None

    model_config = SettingsConfigDict(env_prefix="cors_")


main_settings = MainSettings()
cors_settings = CORSSettings()
