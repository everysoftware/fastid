"""
Test can find cases, when you've changed something in migration and forgot
about models for some reason (or vice versa).
"""

from alembic.autogenerate import compare_metadata
from alembic.command import upgrade
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncConnection

from app.base.models import BaseOrm
from tests.conftest import alembic_config


async def test_migrations_up_to_date(conn: AsyncConnection) -> None:
    def compare(sync_conn: Connection) -> None:
        alembic_config.attributes["connection"] = sync_conn
        upgrade(alembic_config, "head")

        migration_ctx = MigrationContext.configure(sync_conn)
        diff = compare_metadata(migration_ctx, BaseOrm.metadata)
        assert not diff

    await conn.run_sync(compare)
