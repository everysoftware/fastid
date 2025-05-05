from fastid.core.schemas import BaseSettings


class CacheSettings(BaseSettings):
    redis_key: str = "fastid"
    redis_url: str = "redis://default+changethis@localhost:6379/0"


cache_settings = CacheSettings()
