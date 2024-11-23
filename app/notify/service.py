import secrets

from app.auth.config import auth_settings
from app.auth.models import User
from app.authlib.dependencies import token_backend
from app.base.service import UseCase
from app.cache.dependencies import CacheDep
from app.notifier.base import Notification
from app.notifier.dependencies import NotifierDep
from app.notifier.exceptions import WrongCode
from app.notifier.schemas import VerifyTokenRequest
from app.utils.otp import otp


class NotificationUseCases(UseCase):
    def __init__(self, notifier: NotifierDep, cache: CacheDep) -> None:
        self.notifier = notifier
        self.cache = cache
        self.token_backend = token_backend

    async def push(self, notification: Notification) -> None:
        await self.notifier.push(notification)

    async def push_code(self, notification: Notification) -> None:
        code = otp()
        notification.extra["code"] = code
        await self.cache.set(
            f"otp:users:{notification.user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        await self.notifier.push(notification)

    async def validate_code(self, user: User, code: str) -> None:
        user_code = await self.cache.get(f"otp:users:{user.id}", cast=str)
        await self.cache.delete(f"otp:users:{user.id}")
        if user_code is None:
            raise WrongCode()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()

    async def authorize_with_code(
        self, user: User, request: VerifyTokenRequest
    ) -> str:
        await self.validate_code(user, request.code)
        return self.token_backend.create_custom(
            "verify", {"sub": str(user.id)}
        )
