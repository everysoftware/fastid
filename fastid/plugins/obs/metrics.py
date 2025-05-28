import logging

from fastapi import FastAPI
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from starlette.requests import Request
from starlette.responses import Response

from fastid.core.base import Plugin
from fastid.plugins.obs.prometheus import PrometheusMiddleware


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1 and record.getMessage().find("GET /api/v1/metrics") == -1


class MetricsPlugin(Plugin):
    name = "metrics"

    def __init__(self, app_name: str = "fastid") -> None:
        self.app_name = app_name

    def install(self, app: FastAPI) -> None:
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.addFilter(EndpointFilter())
        app.add_middleware(
            PrometheusMiddleware,
            app_name=self.app_name,
        )
        app.add_route("/metrics", get_metrics)


def get_metrics(_request: Request) -> Response:
    return Response(
        generate_latest(REGISTRY),  # type: ignore[no-untyped-call]
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )
