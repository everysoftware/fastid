from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any
from uuid import UUID  # noqa: TCH003

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.database.base import Entity, VersionedEntity

if TYPE_CHECKING:
    from fastid.auth.models import User


class NotificationType(StrEnum):
    email = auto()
    telegram = auto()


class EmailTemplate(VersionedEntity):
    __tablename__ = "email_templates"

    slug: Mapped[str] = mapped_column(unique=True)
    subject: Mapped[str]
    source: Mapped[str]


class TelegramTemplate(VersionedEntity):
    __tablename__ = "telegram_templates"

    slug: Mapped[str] = mapped_column(unique=True)
    source: Mapped[str]


class Notification(Entity):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[NotificationType]
    template: Mapped[str]
    context: Mapped[dict[str, Any]]

    user: Mapped[User] = relationship(back_populates="notifications")
