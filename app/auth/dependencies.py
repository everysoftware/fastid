from typing import Annotated

from fastapi import Depends

from app.auth.models import User
from app.auth.service import AuthUseCases
from app.base.types import UUID

AuthDep = Annotated[AuthUseCases, Depends()]


async def get_user_by_id(service: AuthDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
