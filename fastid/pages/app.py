from typing import Any

from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from fastid.auth.config import auth_settings
from fastid.core.base import MiniApp
from fastid.oauth.clients.dependencies import registry
from fastid.pages.exceptions import add_exception_handlers
from fastid.pages.router import router as pages_router
from fastid.pages.templating import templates

routers = [pages_router]


class FrontendMiniApp(MiniApp):
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
        add_exception_handlers(app)
        app.add_middleware(
            SessionMiddleware,
            secret_key=str(auth_settings.jwt_private_key),
            session_cookie="fastidsession",
        )
        main_router = APIRouter()
        for router in routers:
            main_router.include_router(router)
        app.include_router(main_router)
        return app

    def install(self, app: FastAPI) -> None:
        frontend_app = self.create()
        app.mount(self.static_url, StaticFiles(directory="static"), name="static")
        app.mount(self.base_url, frontend_app)
        app.extra["frontend_app"] = frontend_app

    def _set_templates_env(self) -> None:
        templates.env.globals["app_title"] = self.title
        templates.env.globals["favicon_url"] = self.favicon_url
        templates.env.globals["logo_url"] = self.logo_url
        templates.env.globals["providers_meta"] = registry.metadata
