import logging

from fastapi import FastAPI
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from starlette.requests import Request
from starlette.responses import Response

from app.obs.prometheus import PrometheusMiddleware
from app.main.modules import Plugin


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


class MetricsPlugin(Plugin):
    plugin_name = "metrics"

    def __init__(self, app_name: str = "fastid") -> None:
        self.app_name = app_name

    def install(self, app: FastAPI) -> None:
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.addFilter(EndpointFilter())
        app.add_middleware(
            PrometheusMiddleware,  # noqa
            app_name=self.app_name,
        )
        app.add_route("/metrics", get_metrics)


def get_metrics(request: Request) -> Response:  # noqa
    return Response(
        generate_latest(REGISTRY),  # type: ignore[no-untyped-call]
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )
