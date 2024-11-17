import random
import secrets
import string
from typing import assert_never, Mapping, Any

from app.auth.schemas import UserDTO
from app.auth.config import auth_settings
from app.base.service import UseCases
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.mail.dependencies import MailDep
from app.mail.schemas import MailMessage
from app.notifications.exceptions import WrongCode
from app.notifications.schemas import NotifyMethod, NotifyResponse
from app.telegram.dependencies import BotDep


class NotificationUseCases(UseCases):
    def __init__(
        self, uow: UOWDep, mail: MailDep, bot: BotDep, cache: CacheDep
    ) -> None:
        self.uow = uow
        self.mail = mail
        self.bot = bot
        self.cache = cache

    @staticmethod
    def resolve_method(user: UserDTO) -> NotifyMethod:
        fields: Mapping[str, NotifyMethod] = {
            "telegram_id": "telegram",
            "email": "email",
        }
        for field, method in fields.items():
            if getattr(user, field) is not None:
                return method
        assert False

    def get_sync_response(
        self, user: UserDTO, method: NotifyMethod | None = None
    ) -> NotifyResponse:
        if method is None:
            method = self.resolve_method(user)
        return NotifyResponse(user_id=user.id, method=method, status="sent")

    async def notify(
        self,
        method: NotifyMethod,
        user: UserDTO,
        template: str,
        content: dict[str, Any] | None = None,
    ) -> None:
        content = content if content is not None else {}
        match method:
            case "email":
                msg = MailMessage(
                    subject=content.pop("subject"),
                    template=template,
                    user=user,
                ).as_email(**content)
                return self.mail.send(msg)
            case "telegram":
                assert user.telegram_id is not None
                await self.bot.send_message(user.telegram_id, **content)
            case _:
                assert_never(method)

    async def create_otc(self, user: UserDTO) -> str:
        code = "".join(
            random.choices(string.digits, k=auth_settings.code_length)
        )
        await self.cache.set(
            f"codes:{user.id}", code, expire=auth_settings.code_expires_in
        )
        return code

    async def send_otc(self, method: NotifyMethod, user: UserDTO) -> None:
        code = await self.create_otc(user)
        await self.notify(
            method,
            user,
            "code",
            content={"code": code, "text": f"Your verification code: {code}"},
        )

    async def validate_otc(self, user: UserDTO, code: str) -> None:
        user_code = await self.cache.get(f"otc:{user.id}", cast=str)
        if user_code is None:
            raise WrongCode()
        if not secrets.compare_digest(user_code, code):
            raise WrongCode()
        await self.cache.delete(f"otc:{user.id}")
