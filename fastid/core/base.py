from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI

from fastid.core.dependencies import log


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
    master_app = FastAPI(title=title, **kwargs)

    # Install apps
    for app in apps:
        app.install(master_app)
    installed = [mini_app.name for mini_app in apps]
    log.info("Apps (%d): %s", len(installed), ", ".join(installed))

    return master_app


class UseCase:
    pass
