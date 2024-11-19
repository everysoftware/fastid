import secrets
from abc import ABC, abstractmethod

from app.auth.config import auth_settings
from app.auth.models import User
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.notifier.base import Notification
from app.notifier.exceptions import WrongCode
from app.notifier.mail import MailDep
from app.notifier.telegram import BotDep
from app.utils.otp import otp


class INotifier(ABC):
    @abstractmethod
    async def push(self, notification: Notification) -> None: ...

    @abstractmethod
    async def push_otp(self, notification: Notification) -> None: ...

    @abstractmethod
    async def validate_otp(self, user: User, code: str) -> None: ...


class Notifier(INotifier):
    def __init__(
        self, uow: UOWDep, mail: MailDep, bot: BotDep, cache: CacheDep
    ) -> None:
        self.uow = uow
        self.mail = mail
        self.bot = bot
        self.cache = cache

    async def push(self, notification: Notification) -> None:
        method: str
        if notification.method == "auto":
            method = notification.user.available_contact
        else:
            method = notification.method
        match method:
            case "email":
                return self.mail.send(notification.as_email())
            case "telegram":
                await self.bot.send_message(**notification.as_telegram())
            case _:
                raise ValueError(f"Unknown method: {method}")

    async def push_otp(self, notification: Notification) -> None:
        code = otp()
        notification.extra["code"] = code
        await self.cache.set(
            f"otp:users:{notification.user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        await self.push(notification)

    async def validate_otp(self, user: User, code: str) -> None:
        user_code = await self.cache.get(f"otp:users:{user.id}", cast=str)
        await self.cache.delete(f"otp:users:{user.id}")
        if user_code is None:
            raise WrongCode()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()
