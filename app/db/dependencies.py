from typing import Annotated, AsyncIterator

from fastapi import Depends

from app.db.connection import session_factory
from app.db.uow import AlchemyUOW
from app.base.uow import IUnitOfWork


async def get_uow() -> AsyncIterator[IUnitOfWork]:
    async with AlchemyUOW(session_factory) as uow:
        yield uow


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
