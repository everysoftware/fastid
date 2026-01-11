from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastid.database.config import db_settings
from fastid.database.uow import SQLAlchemyUOW

engine = create_async_engine(
    db_settings.url,
    echo=db_settings.echo,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


def get_uow_raw() -> SQLAlchemyUOW:
    return SQLAlchemyUOW(session_factory)


async def get_uow(uow: Annotated[SQLAlchemyUOW, Depends(get_uow_raw)]) -> AsyncIterator[SQLAlchemyUOW]:
    async with uow:
        yield uow


UOWDep = Annotated[SQLAlchemyUOW, Depends(get_uow)]
UOWRawDep = Annotated[SQLAlchemyUOW, Depends(get_uow_raw)]
