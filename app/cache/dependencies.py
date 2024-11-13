from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.cache.adapter import CacheAdapter
from app.cache.config import cache_settings

redis_client = Redis.from_url(cache_settings.redis_url)


def get_cache() -> CacheAdapter:
    return CacheAdapter(redis_client, key=cache_settings.redis_key)


CacheDep = Annotated[CacheAdapter, Depends(get_cache)]
