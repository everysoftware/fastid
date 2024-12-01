from typing import Sequence, Any

from fastapi import FastAPI

from app.api.exceptions import add_exception_handlers
from app.api.lifespan import LifespanTasks
from app.api.routing import api_router
from app.logging.dependencies import log
from app.main.modules import Module, Plugin


class APIModule(Module):
    module_name = "api"

    def __init__(
        self,
        title: str = "Unnamed App",
        version: str = "0.1.0",
        base_url: str = "/api/v1",
        plugins: Sequence[Plugin] = (),
        **fastapi_kwargs: Any,
    ) -> None:
        self.title = title
        self.version = version
        self.base_url = base_url
        self.plugins = plugins
        self.fastapi_kwargs = fastapi_kwargs

    async def on_startup(self, app: FastAPI) -> None:
        async with LifespanTasks() as tasks:
            await tasks.on_startup()

    async def on_shutdown(self, app: FastAPI) -> None:
        async with LifespanTasks() as tasks:
            await tasks.on_shutdown()

    def install(self, app: FastAPI) -> None:
        api_app = FastAPI(
            title=self.title,
            version=self.version,
            **self.fastapi_kwargs,
        )
        api_app.include_router(api_router)
        add_exception_handlers(api_app)
        for plugin in self.plugins:
            plugin.install(api_app)
        installed = [plugin.plugin_name for plugin in self.plugins]
        log.info("API plugins (%d): %s", len(installed), ", ".join(installed))
        app.mount(self.base_url, api_app)
