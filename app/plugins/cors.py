from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.plugins.base import Plugin


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
