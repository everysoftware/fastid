from typing import Annotated

from fastapi import Depends
from redis.asyncio import BlockingConnectionPool, Redis

from fastid.cache.config import redis_settings
from fastid.cache.storage import RedisStorage

pool = BlockingConnectionPool.from_url(
    redis_settings.url,
    max_connections=redis_settings.pool_size,
    timeout=redis_settings.pool_timeout,
    decode_responses=redis_settings.decode_responses,
    socket_timeout=redis_settings.socket_timeout,
    socket_connect_timeout=redis_settings.socket_connect_timeout,
    retry_on_timeout=redis_settings.retry_on_timeout,
    health_check_interval=redis_settings.health_check_interval,
)
redis_client = Redis.from_pool(pool)


def create_cache() -> RedisStorage:
    return RedisStorage(redis_client, key=redis_settings.major_key)


async def get_cache() -> RedisStorage:
    return create_cache()


CacheDep = Annotated[RedisStorage, Depends(get_cache)]
