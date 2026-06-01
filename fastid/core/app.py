from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastid.admin.app import admin_app
from fastid.api.app import api_app
from fastid.cache.dependencies import get_cache
from fastid.core.config import main_settings
from fastid.core.lifespan import LifespanTasks
from fastid.database.dependencies import get_uow_raw
from fastid.frontend.app import frontend_app


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


core_app = FastAPI(lifespan=lifespan)

core_app.mount(main_settings.api_path, api_app)
core_app.mount(main_settings.admin_path, admin_app)
core_app.mount(main_settings.frontend_path, frontend_app)
