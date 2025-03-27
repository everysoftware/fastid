from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.db.config import db_settings

engine = create_async_engine(
    db_settings.url,
    echo=db_settings.echo,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
