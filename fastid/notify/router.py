from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import JSONResponse

from fastid.auth.dependencies import UserDep, verify_token_transport
from fastid.notify.dependencies import NotifyDep
from fastid.notify.schemas import OTPRequest, VerificationNotification, VerifyTokenRequest

router = APIRouter(prefix="/notify", tags=["Notify"])


@router.post("/otp")
def otp_request(
    user: UserDep,
    service: NotifyDep,
    dto: Annotated[OTPRequest, Depends()],
    background: BackgroundTasks,
) -> None:
    if dto.new_email is None:
        notification = VerificationNotification(user)
    else:
        notification = VerificationNotification(user, method="email", new_email=dto.new_email)
    background.add_task(service.push_code, notification)


@router.post("/verify-token")
async def verify_token_request(
    user: UserDep,
    service: NotifyDep,
    dto: VerifyTokenRequest,
) -> JSONResponse:
    token = await service.authorize_with_code(user, dto)
    response = JSONResponse(content={"verify_token": token})
    verify_token_transport.set_token(response, token)
    return response
