from typing import Annotated

from fastapi import Depends

from app.auth.models import User
from app.auth.service import AuthUseCases
from app.authlib.dependencies import auth_bus
from app.base.types import UUID

AuthDep = Annotated[AuthUseCases, Depends()]


async def get_user(
    service: AuthDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]


async def get_user_by_id(service: AuthDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
