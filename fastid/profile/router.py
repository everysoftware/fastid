from typing import Any

from fastapi import APIRouter, Depends, status

from fastid.auth.dependencies import UserDep
from fastid.auth.permissions import Requires
from fastid.auth.schemas import (
    UserChangeEmail,
    UserChangePassword,
    UserDTO,
    UserUpdate,
)
from fastid.profile.dependencies import ProfilesDep

router = APIRouter(tags=["Users"])


@router.patch("/users/me/profile", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def patch(
    service: ProfilesDep,
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
async def change_email(service: ProfilesDep, user: UserDep, dto: UserChangeEmail) -> Any:
    return await service.change_email(user, dto)


@router.patch(
    "/users/me/password",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(service: ProfilesDep, user: UserDep, dto: UserChangePassword) -> Any:
    return await service.change_password(user, dto)


@router.delete(
    "/users/me",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def delete(service: ProfilesDep, user: UserDep) -> Any:
    return await service.delete_account(user)
