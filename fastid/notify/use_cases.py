import secrets

from auth365.schemas import JWTPayload

from fastid.auth.config import auth_settings
from fastid.auth.models import User
from fastid.cache.dependencies import CacheDep
from fastid.core.base import UseCase
from fastid.notify.clients.dependencies import MailDep, TelegramDep
from fastid.notify.clients.schemas import Notification
from fastid.notify.exceptions import WrongCodeError
from fastid.notify.schemas import VerifyTokenRequest
from fastid.security.crypto import generate_otp
from fastid.security.jwt import jwt_backend


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
        method = notification.user.notification_method if notification.method == "auto" else notification.method
        match method:
            case "email":
                await self.mail.send(notification)
            case "telegram":
                await self.telegram.send(notification)
            case _:
                raise ValueError(f"Unknown method: {method}")

    async def push_code(self, notification: Notification) -> None:
        code = generate_otp()
        notification.extra["code"] = code
        await self.cache.set(
            f"otp:users:{notification.user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        await self.push(notification)

    async def validate_code(self, user: User, code: str) -> None:
        user_code = await self.cache.pop(f"otp:users:{user.id}")
        if user_code is None:
            raise WrongCodeError
        if not secrets.compare_digest(user_code, code):
            raise WrongCodeError

    async def authorize_with_code(self, user: User, request: VerifyTokenRequest) -> str:
        await self.validate_code(user, request.code)
        return jwt_backend.create("verify", JWTPayload(sub=str(user.id)))
