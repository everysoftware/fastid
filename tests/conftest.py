from collections.abc import AsyncIterator

import pytest
from alembic.command import upgrade
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.db.config import db_settings
from app.db.uow import IUnitOfWork, SQLAlchemyUOW
from app.logging.dependencies import provider
from tests.utils.alembic import alembic_config_from_url
from tests.utils.db import delete_all, get_temp_db, get_test_db_url

logger = provider.logger(__name__)
test_db_url = get_test_db_url(db_settings.url)
db_settings.url = test_db_url
alembic_config = alembic_config_from_url(test_db_url)
logger.info("Test database URL: %s", test_db_url)


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    logger.info("Creating temporary database for testing")
    async with get_temp_db(test_db_url):
        logger.info("Temporary database created")
        _engine = create_async_engine(test_db_url, pool_pre_ping=True, poolclass=pool.NullPool)
        yield _engine


@pytest.fixture(scope="session")
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def db_url(engine: AsyncEngine) -> str:
    logger.info("Applying migrations to temporary database")
    upgrade(alembic_config, "head")
    logger.info("Migrated database to latest version")

    return test_db_url


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
def idle_uow(session_factory: async_sessionmaker[AsyncSession]) -> IUnitOfWork:
    return SQLAlchemyUOW(session_factory)


@pytest.fixture
async def uow(idle_uow: IUnitOfWork, engine: AsyncEngine) -> AsyncIterator[IUnitOfWork]:
    async with idle_uow as uow:
        yield uow

    await delete_all(engine)
