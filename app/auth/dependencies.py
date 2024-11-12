from typing import Annotated

from fastapi import Depends

from app.auth.schemas import User
from app.auth.service import AuthUseCases
from app.domain.types import UUID

AuthDep = Annotated[AuthUseCases, Depends()]


async def get_user_by_id(service: AuthDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
