from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from alembic.command import upgrade
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker

from fastid.cache.config import cache_settings
from fastid.cache.dependencies import get_cache
from fastid.cache.storage import CacheStorage, RedisStorage
from fastid.core.app import app
from fastid.core.dependencies import log_provider
from fastid.database.dependencies import get_uow
from fastid.database.uow import SQLAlchemyUOW
from fastid.notify.clients.dependencies import get_bot, get_smtp
from tests.dependencies import (
    alembic_config,
    get_test_cache,
    get_test_uow,
    test_db_url,
    test_engine,
    test_redis,
    test_session_factory,
)
from tests.utils.db import delete_all, get_temp_db

logger = log_provider.logger(__name__)


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    logger.info("Creating temporary database for testing")
    logger.info("Test database URL: %s", test_db_url)
    async with get_temp_db(test_db_url):
        logger.info("Temporary database created")
        yield test_engine


@pytest.fixture(scope="session")
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return test_session_factory


@pytest.fixture(scope="session", autouse=True)
def db_url(engine: AsyncEngine) -> str:
    logger.info("Applying migrations to temporary database")
    upgrade(alembic_config, "head")
    logger.info("Migrated database to latest version")
    return test_db_url


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    api_app = app.extra["api_app"]
    api_app.dependency_overrides[get_uow] = get_test_uow
    api_app.dependency_overrides[get_cache] = get_test_cache
    api_app.dependency_overrides[get_smtp] = lambda: MagicMock()
    api_app.dependency_overrides[get_bot] = lambda: AsyncMock()

    transport = ASGITransport(app=api_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

    api_app.dependency_overrides = {}


@pytest.fixture
async def frontend_client() -> AsyncIterator[AsyncClient]:
    frontend_app = app.extra["frontend_app"]
    frontend_app.dependency_overrides[get_uow] = get_test_uow
    frontend_app.dependency_overrides[get_cache] = get_test_cache

    transport = ASGITransport(app=frontend_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

    frontend_app.dependency_overrides = {}


@pytest.fixture
async def conn(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.begin() as conn:  # type: AsyncConnection
        yield conn


@pytest.fixture
async def session(
    engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session

    await delete_all(engine)


@pytest.fixture
async def uow(session_factory: async_sessionmaker[AsyncSession], engine: AsyncEngine) -> AsyncIterator[SQLAlchemyUOW]:
    async with SQLAlchemyUOW(session_factory) as uow:
        yield uow

    await delete_all(engine)


@pytest.fixture
async def redis_client() -> AsyncIterator[Redis]:
    logger.info("Test redis URL: %s", cache_settings.redis_url)
    yield test_redis
    await test_redis.aclose(close_connection_pool=True)


@pytest.fixture
async def cache(redis_client: Redis) -> AsyncIterator[CacheStorage]:
    yield RedisStorage(redis_client, key=cache_settings.redis_key)
    await test_redis.flushdb()
