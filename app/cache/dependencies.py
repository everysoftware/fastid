from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.cache.adapter import CacheAdapter
from app.runner.config import settings

redis_client = Redis.from_url(settings.cache.redis_url)


def get_cache() -> CacheAdapter:
    return CacheAdapter(redis_client, key=settings.cache.redis_key)


CacheDep = Annotated[CacheAdapter, Depends(get_cache)]
