from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.auth.exceptions import WrongPasswordError
from fastid.auth.schemas import Contact, ContactType
from fastid.database.base import Entity
from fastid.database.utils import uuid
from fastid.notify.config import notify_settings
from fastid.notify.schemas import SendOTPRequest, UserAction
from fastid.oauth.config import telegram_settings
from fastid.security.crypto import crypt_ctx

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from fastid.auth.schemas import UserCreate
    from fastid.notify.models import Notification
    from fastid.oauth.models import OAuthAccount
    from fastid.oauth.schemas import OpenIDBearer


class User(Entity):
    __tablename__ = "users"
    __versioned__: dict[str, Any] = {}

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    email: Mapped[str | None] = mapped_column(index=True)
    telegram_id: Mapped[int | None] = mapped_column(index=True)
    hashed_password: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(back_populates="user", cascade="delete")
    notifications: Mapped[list[Notification]] = relationship(back_populates="user", cascade="delete")

    @hybrid_property
    def is_oauth(self) -> bool:
        return bool(self.hashed_password)

    @hybrid_property
    def display_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        msg = f"User id={self.id} has no available names"
        raise ValueError(msg)

    @classmethod
    def from_create(cls, dto: UserCreate) -> Self:
        user = cls(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
        )
        user.set_password(dto.password)
        return user

    @classmethod
    def from_open_id(cls, open_id: OpenIDBearer) -> Self:
        user = cls(
            id=uuid(),
            first_name=open_id.first_name,
            last_name=open_id.last_name,
            email=open_id.email,
        )
        user.verify()
        user.connect_open_id(open_id)
        return user

    def connect_open_id(self, open_id: OpenIDBearer) -> None:
        if open_id.provider == "telegram":
            self.telegram_id = int(open_id.id)

    def disconnect_open_id(self, provider: str) -> None:
        if provider == "telegram":
            self.telegram_id = None

    def set_password(self, password: str) -> None:
        self.hashed_password = crypt_ctx.hash(password)

    def change_email(self, new_email: str) -> None:
        self.email = new_email

    def verify_password(self, password: str) -> None:
        if not crypt_ctx.verify(password, self.hashed_password):
            raise WrongPasswordError

    def grant_superuser(self) -> None:
        self.is_superuser = True

    def revoke_superuser(self) -> None:
        self.is_superuser = False

    def verify(self) -> None:
        self.is_verified = True

    def is_email_available(self) -> bool:
        return self.email is not None

    def is_telegram_available(self) -> bool:
        return self.telegram_id is not None and telegram_settings.notification_enabled

    def email_contact(self) -> Contact:
        if not self.is_email_available():
            msg = f"User id={self.id} has no available email"
            raise ValueError(msg)
        return Contact(type=ContactType.email, recipient={"email": self.email})

    def telegram_contact(self) -> Contact:
        if not self.is_telegram_available():
            msg = f"User id={self.id} has no available telegram"
            raise ValueError(msg)
        return Contact(type=ContactType.telegram, recipient={"telegram_id": self.telegram_id})

    def find_contacts(self) -> Mapping[ContactType, Contact]:
        contacts = {}
        if self.is_email_available():
            contacts[ContactType.email] = self.email_contact()
        if self.telegram_id is not None and telegram_settings.notification_enabled:
            contacts[ContactType.telegram] = self.telegram_contact()
        if not contacts:
            msg = f"User id={self.id} has no available contacts"
            raise ValueError(msg)
        return contacts

    def sort_contacts(self) -> Sequence[Contact]:
        contacts = list(self.find_contacts().values())
        contacts.sort(key=lambda x: notify_settings.contact_priority[x.type])
        return contacts

    def find_priority_contact(self) -> Contact:
        return self.sort_contacts()[0]

    def find_contact_for_otp(self, dto: SendOTPRequest) -> Contact:
        if dto.action == UserAction.change_email:
            return Contact(type=ContactType.email, recipient={"email": dto.email})
        return self.find_priority_contact()
