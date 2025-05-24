from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import JSONResponse

from fastid.auth.dependencies import UserOrNoneDep, vt_transport
from fastid.notify.dependencies import NotifyDep
from fastid.notify.schemas import SendOTPRequest, VerifyOTPRequest

router = APIRouter()


@router.post("/otp/send", tags=["OTP"])
async def send_otp(
    user: UserOrNoneDep,
    notify_service: NotifyDep,
    dto: Annotated[SendOTPRequest, Depends()],
    background: BackgroundTasks,
) -> None:
    notification = await notify_service.get_otp_notification(user, dto)
    background.add_task(notify_service.push, notification)


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
