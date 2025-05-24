from typing import Any

from fastapi import APIRouter, status

from fastid.auth.dependencies import UserDep, UserVTDep
from fastid.auth.schemas import (
    UserChangeEmail,
    UserChangePassword,
    UserDTO,
    UserUpdate,
)
from fastid.notify.dependencies import NotifyDep
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
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_email(service: ProfilesDep, notify_service: NotifyDep, user: UserVTDep, dto: UserChangeEmail) -> Any:
    await notify_service.validate_otp(user, dto.code)
    return await service.change_email(user, dto)


@router.patch(
    "/users/me/password",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(service: ProfilesDep, user: UserVTDep, dto: UserChangePassword) -> Any:
    return await service.change_password(user, dto)


@router.delete(
    "/users/me",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def delete(service: ProfilesDep, user: UserVTDep) -> Any:
    return await service.delete_account(user)
