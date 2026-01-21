from typing import Any

from fastapi import APIRouter, BackgroundTasks, status

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
async def patch(
    service: ProfilesDep, user: UserDep, dto: UserUpdate, webhooks: WebhooksDep, background: BackgroundTasks
) -> Any:
    user = await service.update_profile(user, dto)
    webhook = SendWebhookRequest(
        type=WebhookType.user_update_profile, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user


@router.patch(
    "/users/me/email",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_email(  # noqa: PLR0913
    service: ProfilesDep,
    notify_service: NotifyDep,
    user: UserVTDep,
    dto: UserChangeEmail,
    webhooks: WebhooksDep,
    background: BackgroundTasks,
) -> Any:
    await notify_service.validate_otp(user, dto.code)
    user = await service.change_email(user, dto)
    webhook = SendWebhookRequest(
        type=WebhookType.user_change_email, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user


@router.patch(
    "/users/me/password",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    service: ProfilesDep, user: UserVTDep, dto: UserChangePassword, webhooks: WebhooksDep, background: BackgroundTasks
) -> Any:
    user = await service.change_password(user, dto)
    webhook = SendWebhookRequest(
        type=WebhookType.user_change_password, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user


@router.delete(
    "/users/me",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def delete(service: ProfilesDep, user: UserVTDep, webhooks: WebhooksDep, background: BackgroundTasks) -> Any:
    user = await service.delete_account(user)
    webhook = SendWebhookRequest(
        type=WebhookType.user_delete, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user
