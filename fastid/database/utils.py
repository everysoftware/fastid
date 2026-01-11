from __future__ import annotations

import datetime
from functools import wraps
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from uuid_utils import uuid7

from fastid.database.uow import SQLAlchemyUOW

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

UUIDv7 = UUID


def uuid() -> UUIDv7:
    return UUIDv7(uuid7().hex)


def uuid_hex() -> str:
    return uuid().hex


def naive_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


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
