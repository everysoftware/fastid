from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.logging.dependencies import log
from app.main.modules import Module


def app_factory(
    *,
    title: str = "Unnamed app",
    modules: Sequence[Module] = (),
    **fastapi_kwargs: Any,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Startup tasks
        for m in modules:
            await m.on_startup(_app)
        yield
        # Shutdown tasks
        for m in modules:
            await m.on_shutdown(_app)

    app = FastAPI(title=title, lifespan=lifespan, **fastapi_kwargs)
    for module in modules:
        module.install(app)
    installed = [module.module_name for module in modules]
    log.info("Installed modules (%d): %s", len(installed), ", ".join(installed))
    return app
