from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.admin.main import app as admin_app
from app.frontend.main import app as frontend_app
from app.runner.api import app as api_app
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


app = FastAPI(lifespan=lifespan)

app.mount("/api", api_app)
app.mount("/admin", admin_app)
app.mount("/", frontend_app)
