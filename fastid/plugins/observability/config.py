from fastid.core.schemas import BaseSettings


class ObservabilitySettings(BaseSettings):
    metrics_enabled: bool = False
    tracing_enabled: bool = False
    otlp_endpoint: str = "http://127.0.0.1:4317"
    service_name: str = "fastid"
    environment: str = "development"


observability_settings = ObservabilitySettings()
