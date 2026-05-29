from fastapi import FastAPI

from fastid.admin.app import admin_app
from fastid.api.app import api_app
from fastid.core.config import main_settings
from fastid.frontend.app import frontend_app

core_app = FastAPI()

core_app.mount(main_settings.api_path, api_app)
core_app.mount(main_settings.admin_path, admin_app)
core_app.mount(main_settings.frontend_path, frontend_app)
