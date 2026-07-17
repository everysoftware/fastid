from __future__ import annotations

import base64
import datetime  # noqa: TCH003 - SQLAlchemy resolves mapped annotations at runtime
import secrets
from enum import auto
from typing import TYPE_CHECKING, Any
from uuid import UUID  # noqa: TCH003

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.core.schemas import BaseEnum
from fastid.database.base import Entity, VersionedEntity

if TYPE_CHECKING:
    from fastid.apps.models import App


def generate_webhook_secret() -> str:
    return f"whsec_{base64.b64encode(secrets.token_bytes(32)).decode()}"


class WebhookType(BaseEnum):
    user_registration = auto()
    user_login = auto()
    user_update_profile = auto()
    user_change_email = auto()
    user_change_password = auto()
    user_delete = auto()


class WebhookDeliveryStatus(BaseEnum):
    pending = auto()
    processing = auto()
    succeeded = auto()
    exhausted = auto()
    cancelled = auto()


class Webhook(VersionedEntity):
    __tablename__ = "webhooks"

    app_id: Mapped[UUID] = mapped_column(ForeignKey("apps.id"), index=True)
    type: Mapped[WebhookType]
    secret: Mapped[str] = mapped_column(default=generate_webhook_secret)
    url: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    disabled_at: Mapped[datetime.datetime | None]
    disabled_reason: Mapped[str | None]

    app: Mapped[App] = relationship(back_populates="webhooks")
    deliveries: Mapped[list[WebhookDelivery]] = relationship(back_populates="webhook", cascade="delete")


class WebhookDelivery(Entity):
    __tablename__ = "webhook_deliveries"

    webhook_id: Mapped[UUID] = mapped_column(ForeignKey("webhooks.id"), index=True)
    event_id: Mapped[UUID] = mapped_column(index=True)
    event_type: Mapped[WebhookType]
    payload: Mapped[dict[str, Any]]
    status: Mapped[WebhookDeliveryStatus] = mapped_column(default=WebhookDeliveryStatus.pending, index=True)
    attempt_count: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime.datetime] = mapped_column(index=True)
    leased_until: Mapped[datetime.datetime | None] = mapped_column(index=True)
    completed_at: Mapped[datetime.datetime | None]
    request: Mapped[dict[str, Any] | None]
    status_code: Mapped[int | None]
    response: Mapped[dict[str, Any] | None]
    error: Mapped[str | None]

    webhook: Mapped[Webhook] = relationship(back_populates="deliveries")
    attempts: Mapped[list[WebhookAttempt]] = relationship(back_populates="delivery", cascade="delete")


class WebhookAttempt(Entity):
    __tablename__ = "webhook_attempts"
    __table_args__ = (UniqueConstraint("delivery_id", "attempt_number"),)

    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("webhook_deliveries.id"), index=True)
    attempt_number: Mapped[int]
    timestamp: Mapped[int]
    request: Mapped[dict[str, Any]]
    status_code: Mapped[int | None]
    response: Mapped[dict[str, Any] | None]
    error: Mapped[str | None]
    duration_ms: Mapped[int]

    delivery: Mapped[WebhookDelivery] = relationship(back_populates="attempts")
