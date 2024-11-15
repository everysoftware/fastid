from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class ObsSettings(BaseSettings):
    enabled: bool = False
    tempo_url: str = "http://host.docker.internal:4317"

    model_config = SettingsConfigDict(env_prefix="obs_")


obs_settings = ObsSettings()
