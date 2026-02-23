from abc import abstractmethod
from collections.abc import Sequence

from fastapi import FastAPI


class AppFactory:
    name = "unknown_app"

    @abstractmethod
    def create(self) -> FastAPI: ...


class Plugin:
    name: str = "unknown_plugin"
    scope: Sequence[str] = ()

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...


class UseCase:
    pass
