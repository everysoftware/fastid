from fastid.api.mini_app import APIMiniApp
from fastid.core.base import MiniApp, Plugin, app_factory
from fastid.core.config import cors_settings, main_settings
from fastid.core.middlewares.cors import CORSPlugin
from fastid.dashboard.config import admin_settings
from fastid.dashboard.mini_app import AdminMiniApp
from fastid.database.dependencies import engine
from fastid.pages.mini_app import FrontendMiniApp
from fastid.plugins.obs.config import obs_settings
from fastid.plugins.obs.metrics import MetricsPlugin
from fastid.plugins.obs.tracing import TracingPlugin

mini_apps: list[MiniApp] = []
api_plugins: list[Plugin] = [
    CORSPlugin(
        origins=cors_settings.origins,
        origin_regex=cors_settings.origin_regex,
    )
]

# Must be last plugin
if obs_settings.enabled:
    api_plugins.extend(
        (
            MetricsPlugin(app_name=main_settings.discovery_name),
            TracingPlugin(
                app_name=main_settings.discovery_name,
                export_url=obs_settings.tempo_url,
                instrument=["logger", "httpx", "sqlalchemy"],
                engine=engine,
            ),
        )
    )

mini_apps.append(
    APIMiniApp(
        title=main_settings.title,
        version=main_settings.version,
        base_url=main_settings.api_path,
        plugins=api_plugins,
    )
)

if admin_settings.enabled:
    mini_apps.append(
        AdminMiniApp(
            engine,
            title=f"{main_settings.title} Admin",
            favicon_url=admin_settings.favicon_url,
            logo_url=admin_settings.logo_url,
        )
    )

# Must be last module
mini_apps.append(FrontendMiniApp(title=main_settings.title))

app = app_factory(
    title=main_settings.title,
    mini_apps=mini_apps,
)
