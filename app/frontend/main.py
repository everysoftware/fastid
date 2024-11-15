from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles

from app.frontend.auth import router as auth_router
from app.main.config import api_settings
from app.main.modules import Module

routers = [auth_router]


class FrontendModule(Module):
    module_name = "frontend"

    def install(self, app: FastAPI) -> None:
        frontend_app = FastAPI(title=api_settings.title)
        frontend_app.mount(
            "/static", StaticFiles(directory="static"), name="static"
        )
        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)

        frontend_app.include_router(main_router)
        app.mount("/app", frontend_app)
