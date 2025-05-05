from collections.abc import AsyncIterator

from redis.asyncio import ConnectionPool, Redis
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastid.cache.config import cache_settings
from fastid.cache.storage import CacheStorage, RedisStorage
from fastid.core.dependencies import log_provider
from fastid.database.config import db_settings
from fastid.database.uow import SQLAlchemyUOW
from tests.utils.alembic import alembic_config_from_url
from tests.utils.db import get_test_db_url

logger = log_provider.logger(__name__)

test_db_url = get_test_db_url(db_settings.url)
db_settings.url = test_db_url
alembic_config = alembic_config_from_url(test_db_url)

test_redis_pool = ConnectionPool.from_url(cache_settings.redis_url)
test_redis = Redis(connection_pool=test_redis_pool)

test_engine = create_async_engine(test_db_url, pool_pre_ping=True, poolclass=pool.NullPool)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


async def get_test_uow() -> AsyncIterator[SQLAlchemyUOW]:
    logger.info("Use get_uow dependency")
    async with SQLAlchemyUOW(test_session_factory) as uow:
        yield uow


def get_test_cache() -> CacheStorage:
    logger.info("Use get_cache dependency")
    return RedisStorage(test_redis, key=cache_settings.redis_key)
