from contextlib import asynccontextmanager
from typing import AsyncIterator, Sequence, Any

from fastapi import FastAPI

from app.api.exceptions import setup_exceptions
from app.api.routing import api_router
from app.plugins.base import Plugin
from app.utils.background import Background


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup tasks
    async with Background() as background:
        await background.healthcheck()
        await background.register_users()
        await background.register_apps()
    yield
    # Shutdown tasks
    # ...


def app_factory(
    *,
    title: str = "Unnamed App",
    version: str = "0.1.0",
    root_path: str = "/api/v1",
    serve_api: bool = True,
    plugins: Sequence[Plugin] = (),
    **fastapi_kwargs: Any,
) -> FastAPI:
    app = FastAPI(
        title=title,
        version=version,
        root_path=root_path,
        lifespan=lifespan,
        **fastapi_kwargs,
    )
    setup_exceptions(app)
    for plugin in plugins:
        plugin.install(app)
    if serve_api:
        app.include_router(api_router)
    return app
