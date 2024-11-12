from fastapi import FastAPI

from app.runner.config import settings
from app.runner.cors import setup_cors
from app.runner.exceptions import setup_exceptions
from app.observability.setup import setup_obs
from app.runner.routing import main_router

app = FastAPI(
    title=settings.app_display_name,
    version=settings.app_version,
    root_path="/api/v1",
)
app.include_router(main_router)

setup_cors(app)
setup_exceptions(app)
setup_obs(app)
