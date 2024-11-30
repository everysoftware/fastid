from typing import Any, Annotated

from fastapi import APIRouter, status, Depends

from app.auth.dependencies import UserManagerDep, UserDep
from app.auth.permissions import Requires
from app.auth.schemas import (
    UserDTO,
    UserUpdate,
    UserCreate,
    UserChangeEmail,
    UserChangePassword,
)

router = APIRouter(tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO
)
async def register(
    service: Annotated[UserManagerDep, Depends()],
    dto: UserCreate,
) -> Any:
    return await service.register(dto)


@router.get(
    "/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK
)
def me(user: UserDep) -> Any:
    return user


@router.patch(
    "/users/me/profile", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def patch(
    service: UserManagerDep,
    user: UserDep,
    dto: UserUpdate,
) -> Any:
    return await service.update_profile(user, dto)


@router.patch(
    "/users/me/email",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_email(
    service: UserManagerDep, user: UserDep, dto: UserChangeEmail
) -> Any:
    return await service.change_email(user, dto)


@router.patch(
    "/users/me/password",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    service: UserManagerDep, user: UserDep, dto: UserChangePassword
) -> Any:
    return await service.change_password(user, dto)


@router.delete(
    "/users/me", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def delete(service: UserManagerDep, user: UserDep) -> Any:
    return await service.delete_account(user)
