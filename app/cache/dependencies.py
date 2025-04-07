from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.cache.adapter import RedisStorage
from app.cache.config import cache_settings

redis_client = Redis.from_url(cache_settings.redis_url)


def get_cache() -> RedisStorage:
    return RedisStorage(redis_client, key=cache_settings.redis_key)


CacheDep = Annotated[RedisStorage, Depends(get_cache)]
