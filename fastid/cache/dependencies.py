from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from fastid.cache.config import redis_settings
from fastid.cache.storage import RedisStorage

redis_client = Redis.from_url(redis_settings.url)


def get_cache() -> RedisStorage:
    return RedisStorage(redis_client, key=redis_settings.major_key)


CacheDep = Annotated[RedisStorage, Depends(get_cache)]
