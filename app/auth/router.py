from typing import Any, Annotated

from fastapi import APIRouter, Form
from starlette import status

from app.auth.dependencies import AuthDep, UserDep
from app.auth.schemas import (
    UserDTO,
    UserUpdate,
    UserCreate,
    OAuth2TokenRequest,
)
from app.authlib.dependencies import cookie_transport
from app.authlib.schemas import TokenResponse

router = APIRouter(tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO
)
async def register(
    service: AuthDep,
    dto: UserCreate,
) -> Any:
    return await service.register(dto)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def authorize(
    service: AuthDep,
    form: Annotated[OAuth2TokenRequest, Form()],
) -> Any:
    token = await service.authorize(form)
    return cookie_transport.get_login_response(token)


@router.get(
    "/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK
)
def me(user: UserDep) -> Any:
    return user


@router.patch(
    "/users/me", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def patch(
    service: AuthDep,
    user: UserDep,
    dto: UserUpdate,
) -> Any:
    return await service.update(user, dto)


@router.delete(
    "/users/me", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def delete(service: AuthDep, user: UserDep) -> Any:
    return await service.delete(user)


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    return cookie_transport.get_logout_response()
