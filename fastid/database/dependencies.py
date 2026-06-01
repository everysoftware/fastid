from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Annotated, Any, cast

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastid.database.config import DBSettings, db_settings
from fastid.database.uow import SQLAlchemyUOW

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Coroutine


def build_connect_args(settings: DBSettings) -> dict[str, Any]:
    args: dict[str, Any] = {
        "server_settings": settings.server_settings,
    }
    if settings.connect_timeout is not None:
        args["timeout"] = settings.connect_timeout
    if settings.command_timeout is not None:
        args["command_timeout"] = settings.command_timeout
    return args


engine = create_async_engine(
    db_settings.url,
    echo=db_settings.echo,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    pool_recycle=db_settings.pool_recycle,
    pool_timeout=db_settings.pool_timeout,
    pool_pre_ping=db_settings.pool_pre_ping,
    connect_args=build_connect_args(db_settings),
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


def get_uow_raw() -> SQLAlchemyUOW:
    return SQLAlchemyUOW(session_factory)


async def get_uow(uow: Annotated[SQLAlchemyUOW, Depends(get_uow_raw)]) -> AsyncIterator[SQLAlchemyUOW]:
    async with uow:
        yield uow


UOWDep = Annotated[SQLAlchemyUOW, Depends(get_uow)]
UOWRawDep = Annotated[SQLAlchemyUOW, Depends(get_uow_raw)]


def transactional[**P, T](_func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(_func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        uow: SQLAlchemyUOW | None = None
        if args:
            use_case: Any = args[0]
            uow = use_case.uow
        if uow is None and kwargs:
            uow = cast(SQLAlchemyUOW, kwargs.get("uow"))
        assert uow is not None

        async with uow:
            return await _func(*args, **kwargs)

        raise AssertionError

    return wrapper
