from typing import Any

from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.auth.config import auth_settings
from app.frontend.exceptions import add_exception_handlers
from app.frontend.pages import router as auth_router
from app.frontend.templating import templates
from app.main.modules import Module
from app.oauth.providers import registry

routers = [auth_router]


class FrontendModule(Module):
    module_name = "frontend"

    def __init__(
        self,
        *,
        title: str = "Unnamed app",
        base_url: str = "/",
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

    def _set_templates_env(self) -> None:
        templates.env.globals["app_title"] = self.title
        templates.env.globals["favicon_url"] = self.favicon_url
        templates.env.globals["logo_url"] = self.logo_url
        templates.env.globals["providers_meta"] = registry.metadata

    def install(self, app: FastAPI) -> None:
        self._set_templates_env()
        frontend_app = FastAPI(title=self.title, **self.fastapi_kwargs)
        add_exception_handlers(frontend_app)
        frontend_app.add_middleware(
            SessionMiddleware,
            secret_key=auth_settings.jwt_private_key,
            session_cookie="fastidsession",
        )
        app.mount(self.static_url, StaticFiles(directory="static"), name="static")
        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)
        frontend_app.include_router(main_router)
        app.mount(self.base_url, frontend_app)
