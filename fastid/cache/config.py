from pydantic_settings import SettingsConfigDict

from fastid.core.config import branding_settings
from fastid.core.schemas import ENV_PREFIX, BaseSettings


class RedisSettings(BaseSettings):
    url: str = "redis://default+changethis@localhost:6379/0"
    major_key: str = branding_settings.service_name

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}redis_")


redis_settings = RedisSettings()
