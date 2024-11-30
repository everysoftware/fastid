from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.backend import auth_bus
from app.auth.models import User
from app.base.types import UUID
from app.profile.service import ProfileUseCases

auth_flows = [
    OAuth2PasswordBearer(
        tokenUrl="auth/token", scheme_name="Password", auto_error=False
    ),
]

UserManagerDep = Annotated[ProfileUseCases, Depends()]


async def get_user(
    service: UserManagerDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]


async def get_user_by_id(service: UserManagerDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
