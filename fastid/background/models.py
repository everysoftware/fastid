from __future__ import annotations

import datetime  # noqa: TCH003 - SQLAlchemy resolves mapped annotations at runtime
from enum import auto
from typing import Any
from uuid import UUID  # noqa: TCH003

from sqlalchemy.orm import Mapped, mapped_column

from fastid.core.schemas import BaseEnum
from fastid.database.base import Entity
from fastid.database.utils import naive_utc


class CPUJobStatus(BaseEnum):
    pending = auto()
    processing = auto()
    succeeded = auto()
    failed = auto()
    cancelled = auto()


class CPUJob(Entity):
    __tablename__ = "cpu_jobs"

    kind: Mapped[str] = mapped_column(index=True)
    payload: Mapped[dict[str, Any]]
    status: Mapped[CPUJobStatus] = mapped_column(default=CPUJobStatus.pending, index=True)
    priority: Mapped[int] = mapped_column(default=0, index=True)
    attempt_count: Mapped[int] = mapped_column(default=0)
    max_attempts: Mapped[int] = mapped_column(default=3)
    next_attempt_at: Mapped[datetime.datetime] = mapped_column(default=naive_utc, index=True)
    leased_until: Mapped[datetime.datetime | None] = mapped_column(index=True)
    lease_token: Mapped[UUID | None] = mapped_column(index=True)
    heartbeat_at: Mapped[datetime.datetime | None]
    started_at: Mapped[datetime.datetime | None]
    completed_at: Mapped[datetime.datetime | None]
    result: Mapped[dict[str, Any] | None]
    error: Mapped[str | None]
