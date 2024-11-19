from fastapi import APIRouter

from app.auth.dependencies import UserDep
from app.notifier.dependencies import NotifierDep
from app.notifier.templates import VerificationNotification

router = APIRouter(prefix="/notifier", tags=["Notifier"])


@router.post("/otc")
async def otc(user: UserDep, notifier: NotifierDep) -> None:
    await notifier.push_otp(VerificationNotification(user))
