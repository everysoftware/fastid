from app.domain.schemas import BaseSettings


class ObservabilitySettings(BaseSettings):
    tempo_url: str = "http://host.docker.internal:4317"
