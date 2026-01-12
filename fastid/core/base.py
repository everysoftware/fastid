from abc import abstractmethod
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from fastid.api.lifespan import LifespanTasks
from fastid.cache.dependencies import get_cache
from fastid.core.dependencies import log
from fastid.database.dependencies import get_uow_raw


class MiniApp:
    name = "unknown_app"

    @abstractmethod
    def create(self) -> FastAPI: ...

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...


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
        tasks = LifespanTasks(uow_factory=get_uow_raw, cache_factory=get_cache)
        async with tasks:
            await tasks.on_startup()
        yield
        # Shutdown tasks
        async with tasks:
            await tasks.on_shutdown()

    master_app = FastAPI(title=title, lifespan=lifespan, **kwargs)

    # Install apps
    for app in apps:
        app.install(master_app)
    installed = [mini_app.name for mini_app in apps]
    log.info("Apps (%d): %s", len(installed), ", ".join(installed))

    return master_app


class UseCase:
    pass
