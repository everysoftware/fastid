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
from fastid.webhooks.dependencies import WebhooksDep
from fastid.webhooks.models import WebhookType
from fastid.webhooks.schemas import SendWebhookRequest

router = APIRouter(tags=["Users"])


@router.patch("/users/me/profile", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def patch(service: ProfilesDep, user: UserDep, dto: UserUpdate, webhooks: WebhooksDep) -> Any:
    user = await service.update_profile(user, dto)
    user_data = UserDTO.model_validate(user).model_dump(mode="json")
    webhook = SendWebhookRequest(type=WebhookType.user_update_profile, payload=user_data | {"user": user_data})
    await webhooks.enqueue(webhook)
    return user


@router.patch(
    "/users/me/email",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_email(
    service: ProfilesDep,
    notify_service: NotifyDep,
    user: UserVTDep,
    dto: UserChangeEmail,
    webhooks: WebhooksDep,
) -> Any:
    await notify_service.validate_otp(user, dto.code)
    user = await service.change_email(user, dto)
    user_data = UserDTO.model_validate(user).model_dump(mode="json")
    webhook = SendWebhookRequest(type=WebhookType.user_change_email, payload=user_data | {"user": user_data})
    await webhooks.enqueue(webhook)
    return user


@router.patch(
    "/users/me/password",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(service: ProfilesDep, user: UserVTDep, dto: UserChangePassword, webhooks: WebhooksDep) -> Any:
    user = await service.change_password(user, dto)
    user_data = UserDTO.model_validate(user).model_dump(mode="json")
    webhook = SendWebhookRequest(type=WebhookType.user_change_password, payload=user_data | {"user": user_data})
    await webhooks.enqueue(webhook)
    return user


@router.delete(
    "/users/me",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def delete(service: ProfilesDep, user: UserVTDep, webhooks: WebhooksDep) -> Any:
    user = await service.delete_account(user)
    user_data = UserDTO.model_validate(user).model_dump(mode="json")
    webhook = SendWebhookRequest(type=WebhookType.user_delete, payload=user_data | {"user": user_data})
    await webhooks.enqueue(webhook)
    return user
