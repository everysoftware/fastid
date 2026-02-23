from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastid.api.exceptions import add_exception_handlers
from fastid.api.lifespan import LifespanTasks
from fastid.api.routing import api_router
from fastid.cache.dependencies import get_cache
from fastid.core.base import AppFactory, Plugin
from fastid.core.dependencies import log
from fastid.database.dependencies import get_uow_raw
from fastid.webhooks.router import router as webhooks_router


class APIAppFactory(AppFactory):
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
        @asynccontextmanager
        async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
            # Startup tasks
            tasks = LifespanTasks(uow_factory=get_uow_raw, cache_factory=get_cache)
            async with tasks:
                await tasks.on_startup()
            yield
            # Shutdown tasks
            async with tasks:
                await tasks.on_shutdown()

        app = FastAPI(
            title=self.title,
            version=self.version,
            webhooks=webhooks_router,
            lifespan=lifespan,
            root_path=self.base_url,
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
