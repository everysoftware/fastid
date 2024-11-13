from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class CORSSettings(BaseSettings):
    origins: list[str] = ["*"]
    origin_regex: str | None = None

    model_config = SettingsConfigDict(env_prefix="cors_")


cors_settings = CORSSettings()
