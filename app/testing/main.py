from fastapi import FastAPI

from app.main.modules import Module
from app.testing.app import app as test_app


class TestAppModule(Module):
    module_name = "test_app"

    def install(self, app: FastAPI) -> None:
        app.mount("/testapp", test_app)
