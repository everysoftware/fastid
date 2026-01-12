import secrets

from fastlink.jwt.schemas import JWTPayload

from fastid.auth.config import auth_settings
from fastid.auth.exceptions import EmailNotFoundError
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.auth.schemas import Contact, ContactType
from fastid.cache.dependencies import CacheDep
from fastid.cache.exceptions import KeyNotFoundError
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWRawDep, transactional
from fastid.database.exceptions import NoResultFoundError
from fastid.notify.clients.dependencies import MailDep, TelegramDep
from fastid.notify.config import jinja_env
from fastid.notify.exceptions import (
    InvalidContactTypeError,
    NoEmailError,
    NoTelegramIDError,
    TemplateNotFoundError,
    WrongCodeError,
)
from fastid.notify.repositories import EmailTemplateSlugSpecification, TelegramTemplateSlugSpecification
from fastid.notify.schemas import (
    PushNotificationRequest,
    SendOTPRequest,
    UserAction,
    VerifyOTPRequest,
)
from fastid.security.crypto import generate_otp
from fastid.security.jwt import jwt_backend


class NotificationUseCases(UseCase):
    def __init__(
        self,
        uow: UOWRawDep,  # Due to background nature of notification use cases, use raw dependency
        mail: MailDep,
        telegram: TelegramDep,
        cache: CacheDep,
    ) -> None:
        self.uow = uow
        self.mail = mail
        self.telegram = telegram
        self.cache = cache

    @transactional
    async def push_email(self, user: User, dto: PushNotificationRequest, contact: Contact | None = None) -> None:
        if contact is None:
            try:
                contact = user.email_contact()
            except ValueError as e:
                raise NoEmailError from e
        assert contact.type == ContactType.email

        base = await self.uow.email_templates.find(EmailTemplateSlugSpecification("base"))
        base_template = jinja_env.from_string(base.source)

        try:
            main = await self.uow.email_templates.find(EmailTemplateSlugSpecification(dto.template_slug))
        except NoResultFoundError as e:
            raise TemplateNotFoundError from e

        main_template = jinja_env.from_string(main.source)
        content = main_template.render(base=base_template, user=user, **dto.template_args)
        await self.mail.send(contact=contact, subject=main.subject, content=content)

    @transactional
    async def push_telegram(self, user: User, dto: PushNotificationRequest, contact: Contact | None = None) -> None:
        if contact is None:
            try:
                contact = user.telegram_contact()
            except ValueError as e:
                raise NoTelegramIDError from e
        assert contact.type == ContactType.telegram

        try:
            template = await self.uow.telegram_templates.find(TelegramTemplateSlugSpecification(dto.template_slug))
        except NoResultFoundError as e:
            raise TemplateNotFoundError from e

        jinja_template = jinja_env.from_string(template.source)
        content = jinja_template.render(user=user, **dto.template_args)
        await self.telegram.send(contact=contact, content=content)

    async def push(self, user: User, dto: PushNotificationRequest, contact: Contact | None = None) -> None:
        if contact is None:
            contact = user.find_priority_contact()
        match contact.type:
            case ContactType.email:
                return await self.push_email(user, dto, contact)
            case ContactType.telegram:
                return await self.push_telegram(user, dto, contact)
            case _:  # pragma: nocover
                raise InvalidContactTypeError

    async def push_otp(self, user: User | None, dto: SendOTPRequest) -> None:
        if dto.action == UserAction.recover_password:
            assert dto.email is not None
            user = await self._get_user_by_email(dto.email)
        assert user is not None
        contact = user.find_contact_for_otp(dto)
        code = await self._generate_otp(user)
        request = PushNotificationRequest(template_slug="code", template_args={"code": code})
        await self.push(user, request, contact)

    async def validate_otp(self, user: User, code: str) -> None:
        try:
            user_code = await self.cache.pop(f"otp:users:{user.id}")
        except KeyNotFoundError as e:
            raise WrongCodeError from e
        if not secrets.compare_digest(user_code, code):
            raise WrongCodeError

    async def verify_otp(self, user: User | None, dto: VerifyOTPRequest) -> str:
        if dto.action == UserAction.recover_password:
            assert dto.email is not None
            user = await self._get_user_by_email(dto.email)
        assert user is not None
        await self.validate_otp(user, dto.code)
        return jwt_backend.create("verify", JWTPayload(sub=str(user.id)))

    @transactional
    async def _get_user_by_email(self, email: str) -> User:
        try:
            return await self.uow.users.find(EmailUserSpecification(email))
        except NoResultFoundError as e:
            raise EmailNotFoundError from e

    async def _generate_otp(self, user: User) -> str:
        code = generate_otp()
        await self.cache.set(
            f"otp:users:{user.id}",
            code,
            expire=auth_settings.verification_code_expires_in,
        )
        return code
