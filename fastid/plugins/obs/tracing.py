from collections.abc import Sequence
from typing import Any, Literal

import uvicorn.logging
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from fastid.core.base import Plugin
from fastid.core.dependencies import log_provider

default_formatter = uvicorn.logging.DefaultFormatter(
    fmt="%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=0 span_id=0 resource.service.name=0] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    use_colors=True,
)
access_formatter = uvicorn.logging.AccessFormatter(
    fmt='%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(client_addr)s - "%(request_line)s" %(status_code)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    use_colors=True,
)
instrumented_formatter = uvicorn.logging.DefaultFormatter(
    fmt="%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    use_colors=True,
)


def patch_logging() -> None:
    log_provider.handler("default").setFormatter(default_formatter)
    log_provider.handler("access").setFormatter(access_formatter)
    log_provider.handler("instrumented").setFormatter(instrumented_formatter)


Instrument = Literal["logger", "httpx", "sqlalchemy"]


class TracingPlugin(Plugin):
    plugin_name = "tracing"

    def __init__(
        self,
        *,
        app_name: str = "unnamed_app",
        export_url: str = "http://localhost:4317",
        instrument: Sequence[Instrument] = ("logger", "httpx"),
        **extra: Any,
    ) -> None:
        self.app_name = app_name
        self.export_url = export_url
        self.instrument = instrument
        self.extra = extra

    def install(self, app: FastAPI) -> None:
        patch_logging()
        resource = Resource.create(
            attributes={
                "service.name": self.app_name,
                "compose_service": self.app_name,
            }
        )
        tracer = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer)
        tracer.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=self.export_url)))
        if "logger" in self.instrument:
            LoggingInstrumentor().instrument(tracer_provider=tracer, set_logging_format=True)
        if "httpx" in self.instrument:
            HTTPXClientInstrumentor().instrument(tracer_provider=tracer)
        if "sqlalchemy" in self.instrument:
            engine = self.extra["engine"]
            if isinstance(engine, AsyncEngine):
                engine = engine.sync_engine
            SQLAlchemyInstrumentor().instrument(
                engine=engine,
                tracer_provider=tracer,
            )
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
