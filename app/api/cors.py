from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings
from app.main.modules import Plugin


class CORSPlugin(Plugin):
    plugin_name = "cors"

    def __init__(
        self,
        *,
        origins: Sequence[str] | None = None,
        origin_regex: str | None = None,
    ) -> None:
        self.origins = origins
        self.origin_regex = origin_regex

    def install(self, app: FastAPI) -> None:
        app.add_middleware(
            CORSMiddleware,  # noqa
            allow_origins=self.origins,
            allow_origin_regex=self.origin_regex,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class CORSSettings(BaseSettings):
    origins: Sequence[str] = ("*",)
    origin_regex: str | None = None

    model_config = SettingsConfigDict(env_prefix="cors_")


cors_settings = CORSSettings()
