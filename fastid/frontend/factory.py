from typing import Any

from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from fastid.auth.config import auth_settings
from fastid.core.base import AppFactory
from fastid.core.config import branding_settings
from fastid.frontend.exceptions import add_exception_handlers
from fastid.frontend.router import router as pages_router
from fastid.frontend.templating import templates
from fastid.oauth.metadata import UI_META

routers = [pages_router]


class FrontendAppFactory(AppFactory):
    name = "frontend"

    def __init__(
        self,
        *,
        title: str = "FastID Frontend",
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

    def create(self) -> FastAPI:
        self._set_templates_env()
        app = FastAPI(title=self.title, **self.fastapi_kwargs)
        app.mount(self.static_url, StaticFiles(directory="static"), name="static")
        add_exception_handlers(app)
        app.add_middleware(
            SessionMiddleware,
            secret_key=str(auth_settings.jwt_key.read_text()),
            session_cookie="fastidsession",
        )
        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)
        app.include_router(main_router)
        return app

    def _set_templates_env(self) -> None:
        templates.env.globals["app_title"] = branding_settings.title
        templates.env.globals["favicon_url"] = self.favicon_url
        templates.env.globals["logo_url"] = self.logo_url
        templates.env.globals["providers_meta"] = UI_META
