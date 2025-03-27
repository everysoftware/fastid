from abc import abstractmethod

from fastapi import FastAPI


class Module:
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
