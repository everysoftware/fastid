import secrets

from auth365.schemas import JWTPayload

from app.auth.backend import token_backend
from app.auth.config import auth_settings
from app.auth.models import User
from app.auth.utils import otp
from app.base.service import UseCase
from app.cache.dependencies import CacheDep
from app.notify.base import Notification
from app.notify.exceptions import WrongCode
from app.notify.mail import MailDep
from app.notify.schemas import VerifyTokenRequest
from app.notify.telegram import TelegramDep


class NotificationUseCases(UseCase):
    def __init__(
        self,
        mail: MailDep,
        telegram: TelegramDep,
        cache: CacheDep,
    ) -> None:
        self.mail = mail
        self.telegram = telegram
        self.cache = cache

    async def push(self, notification: Notification) -> None:
        method: str
        if notification.method == "auto":
            method = notification.user.notification_method
        else:
            method = notification.method
        match method:
            case "email":
                await self.mail.send(notification)
            case "telegram":
                await self.telegram.send(notification)
            case _:
                raise ValueError(f"Unknown method: {method}")

    async def push_code(self, notification: Notification) -> None:
        code = otp()
        notification.extra["code"] = code
        await self.cache.set(
            f"otp:users:{notification.user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        await self.push(notification)

    async def validate_code(self, user: User, code: str) -> None:
        user_code = await self.cache.get(f"otp:users:{user.id}", cast=str)
        await self.cache.delete(f"otp:users:{user.id}")
        if user_code is None:
            raise WrongCode()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()

    async def authorize_with_code(self, user: User, request: VerifyTokenRequest) -> str:
        await self.validate_code(user, request.code)
        return token_backend.create("verify", JWTPayload(sub=str(user.id)))
