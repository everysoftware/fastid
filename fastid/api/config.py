from collections.abc import Sequence

from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class APISettings(BaseSettings):
    cors_origins: Sequence[str] = ("*",)
    cors_origin_regex: str | None = None

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}api_")


api_settings = APISettings()
