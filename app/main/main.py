from app.admin.config import admin_settings
from app.admin.main import AdminModule
from app.api.cors import CORSPlugin, cors_settings
from app.api.main import APIModule
from app.db.connection import engine
from app.frontend.main import FrontendModule
from app.main.config import main_settings
from app.main.factory import app_factory
from app.main.modules import Module, Plugin
from app.obs.config import obs_settings
from app.obs.metrics import MetricsPlugin
from app.obs.tracing import TracingPlugin

modules: list[Module] = []
api_plugins: list[Plugin] = []


if cors_settings.enabled:
    api_plugins.append(
        CORSPlugin(
            origins=cors_settings.origins,
            origin_regex=cors_settings.origin_regex,
        )
    )

# Must be last
if obs_settings.enabled:
    api_plugins.append(MetricsPlugin(app_name=main_settings.discovery_name))
    api_plugins.append(
        TracingPlugin(
            app_name=main_settings.discovery_name,
            export_url=obs_settings.tempo_url,
            instrument=["logger", "httpx", "sqlalchemy"],
            engine=engine,
        )
    )

modules.append(
    APIModule(
        title=main_settings.title,
        version=main_settings.version,
        base_url=main_settings.api_path,
        plugins=api_plugins,
    )
)

if admin_settings.enabled:
    modules.append(
        AdminModule(
            engine,
            title=f"{main_settings.title} Admin",
            favicon_url=admin_settings.favicon_url,
            logo_url=admin_settings.logo_url,
        )
    )

modules.append(FrontendModule(title=main_settings.title))

app = app_factory(
    title=main_settings.title,
    modules=modules,
)
