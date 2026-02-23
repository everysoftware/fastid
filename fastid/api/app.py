from fastid.api.factory import APIAppFactory
from fastid.core.base import Plugin
from fastid.core.config import cors_settings, main_settings
from fastid.database.dependencies import engine
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

api_app = APIAppFactory(
    title=main_settings.title,
    version=main_settings.version,
    base_url=main_settings.api_path,
    allow_origins=cors_settings.origins,
    allow_origin_regex=cors_settings.origin_regex,
    plugins=plugins,
).create()
