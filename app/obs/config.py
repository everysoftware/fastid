from app.base.schemas import BaseSettings


class ObsSettings(BaseSettings):
    tempo_url: str = "http://host.docker.internal:4317"


obs_settings = ObsSettings()
