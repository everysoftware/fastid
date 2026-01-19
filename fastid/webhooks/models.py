from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any
from uuid import UUID  # noqa: TCH003

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.database.base import Entity, VersionedEntity

if TYPE_CHECKING:
    from fastid.apps.models import App


class WebhookType(StrEnum):
    user_registration = auto()
    user_login = auto()
    user_update_profile = auto()
    user_change_email = auto()
    user_change_password = auto()
    user_delete = auto()


class Webhook(VersionedEntity):
    __tablename__ = "webhooks"

    app_id: Mapped[UUID] = mapped_column(ForeignKey("apps.id"), index=True)
    type: Mapped[WebhookType]
    secret: Mapped[str]
    url: Mapped[str]

    app: Mapped[App] = relationship(back_populates="webhooks")
    webhook_events: Mapped[list[WebhookEvent]] = relationship(back_populates="webhook", cascade="delete")


class WebhookEvent(Entity):
    __tablename__ = "webhook_events"

    webhook_id: Mapped[UUID] = mapped_column(ForeignKey("webhooks.id"), index=True)
    request: Mapped[dict[str, Any]]
    status_code: Mapped[int]
    response: Mapped[dict[str, Any]]

    webhook: Mapped[Webhook] = relationship(back_populates="webhook_events")
