import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_utils.functions.database import (
    _set_url_database,
    make_url,
)
from sqlalchemy_utils.functions.orm import quote

from app.db.models import BaseOrm


# Next functions are copied from `sqlalchemy_utils` and slightly modified to support async.
async def create_database_async(_url: str | URL, encoding: str = "utf8", template: str | None = None) -> None:
    url = make_url(_url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_driver = url.get_dialect().driver

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    elif dialect_name == "mssql":
        url = _set_url_database(url, database="master")
    elif dialect_name == "cockroachdb":
        url = _set_url_database(url, database="defaultdb")
    elif dialect_name != "sqlite":
        url = _set_url_database(url, database=None)

    if (dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}) or (
        dialect_name == "postgresql" and dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}
    ):
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    if dialect_name == "postgresql":
        if not template:
            template = "template1"

        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)} ENCODING '{encoding}' TEMPLATE {quote(conn, template)}"
            await conn.execute(sa.text(text))

    elif dialect_name == "mysql":
        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)} CHARACTER SET = '{encoding}'"
            await conn.execute(sa.text(text))

    elif dialect_name == "sqlite" and database != ":memory:":
        if database:
            async with engine.begin() as conn:
                await conn.execute(sa.text("CREATE TABLE DB(id int)"))
                await conn.execute(sa.text("DROP TABLE DB"))

    else:
        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()


async def drop_database_async(_url: str | URL) -> None:
    url = make_url(_url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_driver = url.get_dialect().driver

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    elif dialect_name == "mssql":
        url = _set_url_database(url, database="master")
    elif dialect_name == "cockroachdb":
        url = _set_url_database(url, database="defaultdb")
    elif dialect_name != "sqlite":
        url = _set_url_database(url, database=None)

    if dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}:
        engine = create_async_engine(url, connect_args={"autocommit": True})
    elif dialect_name == "postgresql" and dialect_driver in {
        "asyncpg",
        "pg8000",
        "psycopg2",
        "psycopg2cffi",
    }:
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    if dialect_name == "sqlite" and database != ":memory:":
        if database:
            Path(database).unlink()
    elif dialect_name == "postgresql":
        async with engine.begin() as conn:
            # Disconnect all users from the database we are dropping.
            version = conn.dialect.server_version_info
            pid_column = "pid" if (version >= (9, 2)) else "procpid"  # type: ignore[operator]
            text = f"""
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
            """  # noqa: S608
            await conn.execute(sa.text(text))

            # Drop the database.
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))
    else:
        async with engine.begin() as conn:
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()


# Clean tables after each test. I tried:
# 1. Create new database using an empty `migrated_postgres_template` as template
# (postgres could copy whole db structure)
# 2. Do TRUNCATE after each test.
# 3. Do DELETE after each test.
# DELETE FROM is the fastest
# https://www.lob.com/blog/truncate-vs-delete-efficiently-clearing-data-from-a-postgres-table
# BUT DELETE FROM query does not reset any AUTO_INCREMENT counter
async def delete_all(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        for table in reversed(BaseOrm.metadata.sorted_tables):
            # Clean tables in such order that tables which depend on another go first
            await conn.execute(table.delete())
        await conn.commit()


def get_test_db_url(source_db_url: str) -> str:
    url = make_url(source_db_url)
    url = url.set(database=f"test_{uuid.uuid4().hex}")
    return url.render_as_string(hide_password=False)  # type: ignore[no-any-return]


@asynccontextmanager
async def get_temp_db(db_url: str | URL) -> AsyncIterator[None]:
    await create_database_async(db_url)
    try:
        yield
    finally:
        await drop_database_async(db_url)
