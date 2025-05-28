from abc import abstractmethod
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from fastid.core.dependencies import log


class MiniApp:
    name = "unknown_app"

    @abstractmethod
    def create(self) -> FastAPI: ...

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...

    async def on_startup(self, app: FastAPI) -> None:
        pass

    async def on_shutdown(self, app: FastAPI) -> None:
        pass


class Plugin:
    name: str = "unknown_plugin"
    scope: Sequence[str] = ()

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...


def app_factory(
    *,
    title: str = "FastID",
    apps: Sequence[MiniApp] = (),
    **kwargs: Any,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Startup tasks
        for m in apps:
            await m.on_startup(_app)
        yield
        # Shutdown tasks
        for m in apps:
            await m.on_shutdown(_app)

    master_app = FastAPI(title=title, lifespan=lifespan, **kwargs)

    # Install apps
    for app in apps:
        app.install(master_app)
    installed = [mini_app.name for mini_app in apps]
    log.info("Apps (%d): %s", len(installed), ", ".join(installed))

    return master_app


class UseCase:
    pass
