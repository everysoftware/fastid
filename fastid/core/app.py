from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastid.admin.app import admin_app
from fastid.api.app import api_app
from fastid.cache.dependencies import create_cache
from fastid.core.config import core_settings
from fastid.core.debug import debug_router
from fastid.core.health import health_router
from fastid.core.lifespan import LifespanTasks
from fastid.database.dependencies import create_uow, engine
from fastid.frontend.app import frontend_app
from fastid.plugins.observability.metrics import get_metrics


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup tasks
    tasks = LifespanTasks(uow_factory=create_uow, cache_factory=create_cache)
    try:
        async with tasks:
            await tasks.on_startup()
        yield
    finally:
        try:
            await tasks.on_shutdown()
        finally:
            await engine.dispose()


core_app = FastAPI(lifespan=lifespan)

core_app.add_route(
    "/metrics",
    get_metrics,
    include_in_schema=False,
)

core_app.include_router(health_router)
core_app.include_router(debug_router)

core_app.mount(core_settings.api_path, api_app)
core_app.mount(core_settings.admin_path, admin_app)
core_app.mount(core_settings.frontend_path, frontend_app)
