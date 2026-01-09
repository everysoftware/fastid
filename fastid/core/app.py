from fastid.admin.app import AdminMiniApp
from fastid.admin.config import admin_settings
from fastid.api.app import APIMiniApp
from fastid.core.base import Plugin, app_factory
from fastid.core.config import cors_settings, main_settings
from fastid.database.dependencies import engine
from fastid.pages.app import FrontendMiniApp
from fastid.plugins.obs.config import obs_settings
from fastid.plugins.obs.metrics import MetricsPlugin
from fastid.plugins.obs.tracing import TracingPlugin

plugins: list[Plugin] = []

# Must be last plugin
if obs_settings.enabled:
    metrics_plugin = MetricsPlugin(app_name=main_settings.discovery_name)
    tracing_plugin = TracingPlugin(
        app_name=main_settings.discovery_name,
        export_url=obs_settings.tempo_url,
        instrument=["logger", "httpx", "sqlalchemy"],
        engine=engine,
    )
    plugins += [metrics_plugin, tracing_plugin]

api_app = APIMiniApp(
    title=main_settings.title,
    version=main_settings.version,
    base_url=main_settings.api_path,
    allow_origins=cors_settings.origins,
    allow_origin_regex=cors_settings.origin_regex,
    plugins=plugins,
)
admin_app = AdminMiniApp(
    engine,
    title=f"{main_settings.title} Admin",
    favicon_url=admin_settings.favicon_url,
    logo_url=admin_settings.logo_url,
)
frontend_app = FrontendMiniApp(title=main_settings.title)

app = app_factory(
    title=main_settings.title,
    apps=[api_app, admin_app, frontend_app],
)
