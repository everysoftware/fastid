from pydantic_settings import SettingsConfigDict

from fastid.core.config import branding_settings
from fastid.core.schemas import ENV_PREFIX, BaseSettings


class RedisSettings(BaseSettings):
    url: str = "redis://default+changethis@localhost:6379/0"
    major_key: str = branding_settings.service_name
    decode_responses: bool = True
    pool_size: int = 50
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    socket_keepalive: bool = True
    retry_on_timeout: bool = True
    health_check_interval: int = 30

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}redis_")


redis_settings = RedisSettings()
