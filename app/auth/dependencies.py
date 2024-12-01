from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.exceptions import ClientError
from app.auth.backend import auth_bus
from app.auth.models import User
from app.auth.service import AuthUseCases

auth_flows = [
    OAuth2PasswordBearer(
        tokenUrl="auth/token", scheme_name="Password", auto_error=False
    ),
]

AuthDep = Annotated[AuthUseCases, Depends()]


async def get_user(
    service: AuthDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]


async def get_optional_user(service: AuthDep, request: Request) -> User | None:
    token = auth_bus.parse_request(request, auto_error=False)
    if token is None:
        return None
    try:
        return await service.get_userinfo(token)
    except ClientError:
        return None
