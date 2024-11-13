from abc import ABC, abstractmethod

from fastapi import FastAPI


class Plugin(ABC):
    plugin_name: str = "unknown"

    @abstractmethod
    def install(self, app: FastAPI) -> None: ...
