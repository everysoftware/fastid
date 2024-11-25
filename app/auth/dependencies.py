from typing import Annotated

from fastapi import Depends

from app.auth.models import User
from app.auth.service import UserManagementUseCases
from app.authlib.dependencies import auth_bus
from app.base.types import UUID

UserManagerDep = Annotated[UserManagementUseCases, Depends()]


async def get_user(
    service: UserManagerDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]


async def get_user_by_id(service: UserManagerDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
