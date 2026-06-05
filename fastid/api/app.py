from fastid.api.config import api_settings
from fastid.api.factory import APIAppFactory
from fastid.core.base import Plugin
from fastid.core.config import branding_settings, core_settings
from fastid.database.dependencies import engine
from fastid.plugins.observability.config import observability_settings
from fastid.plugins.observability.metrics import MetricsPlugin
from fastid.plugins.observability.tracing import TracingPlugin

plugins: list[Plugin] = []

# Must be last plugins
if observability_settings.metrics_enabled:
    metrics_plugin = MetricsPlugin(app_name=branding_settings.service_name)
    plugins.append(metrics_plugin)
if observability_settings.tracing_enabled:
    tracing_plugin = TracingPlugin(
        app_name=branding_settings.service_name,
        export_url=observability_settings.tempo_url,
        instrument=["logger", "httpx", "sqlalchemy"],
        engine=engine,
    )
    plugins.append(tracing_plugin)

api_app = APIAppFactory(
    title=branding_settings.api_swagger_title,
    base_url=core_settings.api_path,
    allow_origins=api_settings.cors_origins,
    allow_origin_regex=api_settings.cors_origin_regex,
    plugins=plugins,
).create()
