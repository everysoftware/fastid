from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles

from app.frontend.auth import router as auth_router
from app.plugins.base import Plugin

routers = [auth_router]


class FrontendPlugin(Plugin):
    plugin_name = "frontend"

    def install(self, app: FastAPI) -> None:
        app.mount("/static", StaticFiles(directory="static"), name="static")

        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)

        app.include_router(main_router)
