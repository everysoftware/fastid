from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from fastid.database.base import Entity


class EmailTemplate(Entity):
    __tablename__ = "email_templates"

    slug: Mapped[str] = mapped_column(unique=True)
    subject: Mapped[str]
    source: Mapped[str]


class TelegramTemplate(Entity):
    __tablename__ = "telegram_templates"

    slug: Mapped[str] = mapped_column(unique=True)
    source: Mapped[str]
