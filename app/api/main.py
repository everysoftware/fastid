from app.admin.main import AdminPlugin
from app.api.config import api_settings
from app.api.factory import app_factory
from app.db.connection import engine
from app.frontend.main import FrontendPlugin
from app.obs.config import obs_settings
from app.obs.metrics import MetricsPlugin
from app.obs.tracing import TracingPlugin
from app.plugins.config import cors_settings
from app.plugins.cors import CORSPlugin

app = app_factory(
    title=api_settings.title,
    version=api_settings.version,
    root_path=api_settings.root_path,
    plugins=[
        CORSPlugin(
            origins=cors_settings.origins,
            origin_regex=cors_settings.origin_regex,
        ),
        MetricsPlugin(app_name=api_settings.discovery_name),
        AdminPlugin(
            engine,
            favicon_url=f"{api_settings.root_path}/static/assets/favicon.ico",
            title=f"Admin | {api_settings.title}",
        ),
        FrontendPlugin(),
        # Must be last
        TracingPlugin(
            app_name=api_settings.discovery_name,
            export_url=obs_settings.tempo_url,
            instrument=["logger", "httpx", "sqlalchemy"],
            engine=engine,
        ),
    ],
)
