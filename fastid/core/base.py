from abc import abstractmethod
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from fastid.core.dependencies import log


class MiniApp:
    module_name = "unknown_module"

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...

    async def on_startup(self, app: FastAPI) -> None:
        pass

    async def on_shutdown(self, app: FastAPI) -> None:
        pass


class Plugin:
    plugin_name: str = "unknown_plugin"

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...


def app_factory(
    *,
    title: str = "Unknown app",
    mini_apps: Sequence[MiniApp] = (),
    **kwargs: Any,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Startup tasks
        for m in mini_apps:
            await m.on_startup(_app)
        yield
        # Shutdown tasks
        for m in mini_apps:
            await m.on_shutdown(_app)

    app = FastAPI(title=title, lifespan=lifespan, **kwargs)
    for mini_app in mini_apps:
        mini_app.install(app)
    installed = [mini_app.module_name for mini_app in mini_apps]
    log.info("Mini apps (%d): %s", len(installed), ", ".join(installed))
    return app


class UseCase:
    pass
