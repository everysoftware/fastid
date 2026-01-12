from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import JSONResponse

from fastid.auth.dependencies import UserDep, UserOrNoneDep, vt_transport
from fastid.notify.dependencies import NotifyDep
from fastid.notify.schemas import PushNotificationRequest, SendOTPRequest, VerifyOTPRequest

router = APIRouter(tags=["Notifications"])


@router.post("/email/send")
async def send_email(
    user: UserDep,
    notify_service: NotifyDep,
    dto: PushNotificationRequest,
    background: BackgroundTasks,
) -> None:
    background.add_task(notify_service.push_email, user, dto)


@router.post("/telegram/send")
async def send_telegram(
    user: UserDep,
    notify_service: NotifyDep,
    dto: PushNotificationRequest,
    background: BackgroundTasks,
) -> None:
    background.add_task(notify_service.push_telegram, user, dto)


@router.post("/otp/send", tags=["OTP"])
async def send_otp(
    user: UserOrNoneDep,
    notify_service: NotifyDep,
    dto: Annotated[SendOTPRequest, Depends()],
    background: BackgroundTasks,
) -> None:
    background.add_task(notify_service.push_otp, user, dto)


@router.post("/otp/verify", tags=["OTP"])
async def verify_otp(
    user: UserOrNoneDep,
    notify_service: NotifyDep,
    dto: VerifyOTPRequest,
) -> JSONResponse:
    token = await notify_service.verify_otp(user, dto)
    response = JSONResponse(content={"verify_token": token})
    vt_transport.set_token(response, token)
    return response
