import secrets

from fastlink.jwt.schemas import JWTPayload

from fastid.auth.config import auth_settings
from fastid.auth.exceptions import EmailNotFoundError
from fastid.auth.models import User
from fastid.auth.repositories import UserEmailSpecification
from fastid.cache.dependencies import CacheDep
from fastid.cache.exceptions import KeyNotFoundError
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.notify.clients.dependencies import MailDep, TelegramDep
from fastid.notify.clients.schemas import Notification
from fastid.notify.exceptions import WrongCodeError
from fastid.notify.schemas import OTPNotification, SendOTPRequest, UnsafeAction, VerifyOTPRequest
from fastid.security.crypto import generate_otp
from fastid.security.jwt import jwt_backend


class NotificationUseCases(UseCase):
    def __init__(
        self,
        uow: UOWDep,
        mail: MailDep,
        telegram: TelegramDep,
        cache: CacheDep,
    ) -> None:
        self.uow = uow
        self.mail = mail
        self.telegram = telegram
        self.cache = cache

    async def get_otp_notification(self, user: User | None, dto: SendOTPRequest) -> OTPNotification:
        if dto.action == UnsafeAction.recover_password:
            assert dto.email is not None
            user = await self._get_user_by_email(dto.email)
        assert user is not None
        if dto.action in UnsafeAction.change_email:
            notification = OTPNotification(user, method="email", email_override=dto.email)
        else:
            notification = OTPNotification(user)
        notification.extra["code"] = await self._get_otp(user)
        return notification

    async def push(self, notification: Notification) -> None:
        method: str
        method = notification.user.notification_method if notification.method == "auto" else notification.method
        match method:
            case "email":
                await self.mail.send(notification)
            case "telegram":
                await self.telegram.send(notification)
            case _:  # pragma: nocover
                raise ValueError(f"Unknown method: {method}")

    async def validate_otp(self, user: User, code: str) -> None:
        try:
            user_code = await self.cache.pop(f"otp:users:{user.id}")
        except KeyNotFoundError as e:
            raise WrongCodeError from e
        if not secrets.compare_digest(user_code, code):
            raise WrongCodeError

    async def verify_otp(self, user: User | None, dto: VerifyOTPRequest) -> str:
        if dto.action == UnsafeAction.recover_password:
            assert dto.email is not None
            user = await self._get_user_by_email(dto.email)
        assert user is not None
        await self.validate_otp(user, dto.code)
        return jwt_backend.create("verify", JWTPayload(sub=str(user.id)))

    async def _get_user_by_email(self, email: str) -> User:
        try:
            return await self.uow.users.find(UserEmailSpecification(email))
        except NoResultFoundError as e:
            raise EmailNotFoundError from e

    async def _get_otp(self, user: User) -> str:
        code = generate_otp()
        await self.cache.set(
            f"otp:users:{user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        return code
