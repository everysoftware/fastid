from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends

from app.db.connection import session_factory
from app.db.uow import IUnitOfWork, SQLAlchemyUOW


async def get_uow() -> AsyncIterator[IUnitOfWork]:
    async with SQLAlchemyUOW(session_factory) as uow:
        yield uow


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
