from fastapi import FastAPI

from app.runner.config import settings
from app.db.connection import async_engine
from app.observability.metrics import PrometheusMiddleware, get_metrics
from app.observability.tracing import instrument


def setup_obs(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware, app_name=settings.app_name)  # noqa
    app.add_route("/metrics", get_metrics)
    instrument(
        app,
        async_engine,
        export_url=settings.obs.tempo_url,
        app_name=settings.app_name,
    )
