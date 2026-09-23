from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select, update

from fastid.background.models import CPUJob, CPUJobStatus
from fastid.database.repository import SQLAlchemyRepository
from fastid.database.utils import naive_utc, uuid


@dataclass(frozen=True)
class ClaimedCPUJob:
    id: UUID
    kind: str
    payload: dict[str, Any]
    lease_token: UUID
    attempt_count: int
    max_attempts: int


class CPUJobRepository(SQLAlchemyRepository[CPUJob]):
    model_type = CPUJob

    async def claim(self, limit: int, lease_seconds: int) -> list[ClaimedCPUJob]:
        now = naive_utc()
        leased_until = now + timedelta(seconds=lease_seconds)
        stmt = (
            select(CPUJob)
            .where(
                CPUJob.next_attempt_at <= now,
                or_(
                    CPUJob.status == CPUJobStatus.pending,
                    (CPUJob.status == CPUJobStatus.processing) & (CPUJob.leased_until <= now),
                ),
            )
            .order_by(CPUJob.priority.desc(), CPUJob.next_attempt_at, CPUJob.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        jobs = list((await self.session.scalars(stmt)).all())
        claims: list[ClaimedCPUJob] = []
        for job in jobs:
            token = uuid()
            job.status = CPUJobStatus.processing
            job.attempt_count += 1
            job.leased_until = leased_until
            job.lease_token = token
            job.heartbeat_at = now
            if job.started_at is None:
                job.started_at = now
            claims.append(
                ClaimedCPUJob(
                    id=job.id,
                    kind=job.kind,
                    payload=job.payload,
                    lease_token=token,
                    attempt_count=job.attempt_count,
                    max_attempts=job.max_attempts,
                )
            )
        await self.session.flush()
        return claims

    async def heartbeat(self, job_id: UUID, lease_token: UUID, lease_seconds: int) -> bool:
        now = naive_utc()
        return await self._owned_update(
            job_id,
            lease_token,
            leased_until=now + timedelta(seconds=lease_seconds),
            heartbeat_at=now,
        )

    async def succeed(self, job_id: UUID, lease_token: UUID, result: dict[str, Any]) -> bool:
        return await self._owned_update(
            job_id,
            lease_token,
            status=CPUJobStatus.succeeded,
            result=result,
            error=None,
            completed_at=naive_utc(),
            leased_until=None,
            lease_token=None,
        )

    async def retry(self, job_id: UUID, lease_token: UUID, error: str, next_attempt_at: datetime) -> bool:
        return await self._owned_update(
            job_id,
            lease_token,
            status=CPUJobStatus.pending,
            error=error,
            next_attempt_at=next_attempt_at,
            leased_until=None,
            lease_token=None,
        )

    async def fail(self, job_id: UUID, lease_token: UUID, error: str) -> bool:
        return await self._owned_update(
            job_id,
            lease_token,
            status=CPUJobStatus.failed,
            error=error,
            completed_at=naive_utc(),
            leased_until=None,
            lease_token=None,
        )

    async def cancel(self, job_id: UUID) -> bool:
        stmt = (
            update(CPUJob)
            .where(CPUJob.id == job_id, CPUJob.status == CPUJobStatus.pending)
            .values(
                status=CPUJobStatus.cancelled,
                completed_at=naive_utc(),
                leased_until=None,
                lease_token=None,
            )
            .returning(CPUJob.id)
        )
        return await self.session.scalar(stmt) is not None

    async def _owned_update(self, job_id: UUID, ownership_token: UUID, **values: object) -> bool:
        stmt = (
            update(CPUJob)
            .where(
                CPUJob.id == job_id,
                CPUJob.status == CPUJobStatus.processing,
                CPUJob.lease_token == ownership_token,
            )
            .values(**values)
            .returning(CPUJob.id)
        )
        return await self.session.scalar(stmt) is not None
