from typing import Any

from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles

from app.frontend.auth import router as auth_router
from app.frontend.templating import templates
from app.main.config import main_settings
from app.main.modules import Module

routers = [auth_router]


class FrontendModule(Module):
    module_name = "frontend"

    def __init__(
        self,
        *,
        title: str = "Unnamed app",
        base_url: str = "/app",
        static_url: str = "/static",
        favicon_url: str = "/static/assets/favicon.png",
        logo_url: str = "/static/assets/logo.png",
        **fastapi_kwargs: Any,
    ) -> None:
        self.title = title
        self.base_url = base_url
        self.favicon_url = favicon_url
        self.logo_url = logo_url
        self.static_url = static_url
        self.fastapi_kwargs = fastapi_kwargs

    def _update_env(self) -> None:
        templates.env.globals["app_title"] = self.title
        templates.env.globals["favicon_url"] = self.favicon_url
        templates.env.globals["logo_url"] = self.logo_url
        templates.env.globals["google_login_url"] = (
            f"{main_settings.oauth_login_url}/google"
        )
        templates.env.globals["yandex_login_url"] = (
            f"{main_settings.oauth_login_url}/yandex"
        )
        templates.env.globals["telegram_login_url"] = (
            f"{main_settings.oauth_login_url}/telegram"
        )

    def install(self, app: FastAPI) -> None:
        self._update_env()
        frontend_app = FastAPI(title=self.title, **self.fastapi_kwargs)
        app.mount(
            self.static_url, StaticFiles(directory="static"), name="static"
        )
        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)

        frontend_app.include_router(main_router)
        app.mount(self.base_url, frontend_app)
