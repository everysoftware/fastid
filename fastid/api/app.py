from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastid.api.exceptions import add_exception_handlers
from fastid.api.routing import api_router
from fastid.core.base import MiniApp, Plugin
from fastid.core.dependencies import log
from fastid.webhooks.router import router as webhooks_router


class APIMiniApp(MiniApp):
    name = "api"

    def __init__(  # noqa: PLR0913
        self,
        title: str = "FastID API",
        version: str = "0.1.0",
        base_url: str = "/api/v1",
        allow_origins: Sequence[str] = ("*",),
        allow_origin_regex: str | None = None,
        plugins: Sequence[Plugin] = (),
        **fastapi_kwargs: Any,
    ) -> None:
        self.title = title
        self.version = version
        self.base_url = base_url
        self.allow_origins = allow_origins
        self.allow_origin_regex = allow_origin_regex
        self.plugins = plugins
        self.fastapi_kwargs = fastapi_kwargs

    def create(self) -> FastAPI:
        app = FastAPI(
            title=self.title,
            version=self.version,
            webhooks=webhooks_router,
            **self.fastapi_kwargs,
        )
        app.include_router(api_router)
        add_exception_handlers(app)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allow_origins,
            allow_origin_regex=self.allow_origin_regex,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        for plugin in self.plugins:
            plugin.install(app)
        installed = [plugin.name for plugin in self.plugins]
        log.info("Plugins (%d): %s", len(installed), ", ".join(installed))

        return app

    def install(self, app: FastAPI) -> None:
        api_app = self.create()
        app.mount(self.base_url, api_app)
        app.extra["api_app"] = api_app
