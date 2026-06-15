from fastid.core.schemas import BaseSettings


class ObservabilitySettings(BaseSettings):
    metrics_enabled: bool = False
    tracing_enabled: bool = False
    tempo_url: str = "http://host.docker.internal:4317"


observability_settings = ObservabilitySettings()
