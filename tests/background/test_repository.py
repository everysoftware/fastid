from datetime import timedelta

from fastid.background.models import CPUJob
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc, uuid

CLAIM_LIMIT = 3
DEFAULT_MAX_ATTEMPTS = 3
SECOND_ATTEMPT = 2


async def test_claim_orders_due_jobs_and_sets_ownership(uow: SQLAlchemyUOW) -> None:
    now = naive_utc()
    low = CPUJob(kind="low", payload={}, priority=1, next_attempt_at=now)
    high_later = CPUJob(
        kind="high-later",
        payload={},
        priority=10,
        next_attempt_at=now,
        created_at=now + timedelta(seconds=1),
    )
    high_first = CPUJob(
        kind="high-first",
        payload={},
        priority=10,
        next_attempt_at=now,
        created_at=now,
    )
    future = CPUJob(kind="future", payload={}, priority=100, next_attempt_at=now + timedelta(hours=1))
    for job in (low, high_later, high_first, future):
        await uow.cpu_jobs.add(job)

    claims = await uow.cpu_jobs.claim(limit=CLAIM_LIMIT, lease_seconds=60)

    assert [claim.id for claim in claims] == [high_first.id, high_later.id, low.id]
    assert len({claim.lease_token for claim in claims}) == CLAIM_LIMIT
    assert all(claim.attempt_count == 1 for claim in claims)
    assert all(claim.max_attempts == DEFAULT_MAX_ATTEMPTS for claim in claims)
    for job in (low, high_later, high_first):
        await uow.session.refresh(job)
        assert job.status == "processing"
        assert job.attempt_count == 1
        assert job.lease_token is not None
        assert job.leased_until is not None
        assert job.heartbeat_at is not None
        assert job.started_at is not None
    await uow.session.refresh(future)
    assert future.status == "pending"


async def test_heartbeat_requires_current_lease_token(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="heartbeat", payload={}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    claim = (await uow.cpu_jobs.claim(limit=1, lease_seconds=1))[0]
    original_lease = job.leased_until

    assert await uow.cpu_jobs.heartbeat(job.id, uuid(), lease_seconds=60) is False
    assert await uow.cpu_jobs.heartbeat(job.id, claim.lease_token, lease_seconds=60) is True

    await uow.session.refresh(job)
    assert job.status == "processing"
    assert job.leased_until is not None
    assert original_lease is not None
    assert job.leased_until > original_lease


async def test_completion_requires_current_lease_token(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="complete", payload={}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    claim = (await uow.cpu_jobs.claim(limit=1, lease_seconds=60))[0]

    assert await uow.cpu_jobs.succeed(job.id, uuid(), {"wrong": True}) is False
    await uow.session.refresh(job)
    assert job.status == "processing"
    assert job.result is None

    assert await uow.cpu_jobs.succeed(job.id, claim.lease_token, {"ok": True}) is True
    await uow.session.refresh(job)
    assert job.status == "succeeded"
    assert job.result == {"ok": True}
    assert job.completed_at is not None
    assert job.lease_token is None
    assert job.leased_until is None


async def test_retry_fail_and_cancel_transitions(uow: SQLAlchemyUOW) -> None:
    retry_job = CPUJob(kind="retry", payload={}, next_attempt_at=naive_utc())
    fail_job = CPUJob(kind="fail", payload={}, next_attempt_at=naive_utc())
    cancelled_job = CPUJob(kind="cancel", payload={}, next_attempt_at=naive_utc())
    for job in (retry_job, fail_job, cancelled_job):
        await uow.cpu_jobs.add(job)
    retry_claim, fail_claim = await uow.cpu_jobs.claim(limit=2, lease_seconds=60)
    retry_at = naive_utc() + timedelta(minutes=5)

    assert await uow.cpu_jobs.retry(retry_claim.id, retry_claim.lease_token, "try again", retry_at) is True
    assert await uow.cpu_jobs.fail(fail_claim.id, fail_claim.lease_token, "broken") is True
    assert await uow.cpu_jobs.cancel(cancelled_job.id) is True
    assert await uow.cpu_jobs.cancel(retry_job.id) is True
    assert await uow.cpu_jobs.cancel(fail_job.id) is False

    for job in (retry_job, fail_job, cancelled_job):
        await uow.session.refresh(job)
    assert retry_job.status == "cancelled"
    assert retry_job.error == "try again"
    assert fail_job.status == "failed"
    assert fail_job.error == "broken"
    assert fail_job.completed_at is not None
    assert cancelled_job.status == "cancelled"
    assert cancelled_job.completed_at is not None


async def test_expired_processing_job_is_reclaimed_with_new_token(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="reclaim", payload={"value": 1}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    first = (await uow.cpu_jobs.claim(limit=1, lease_seconds=60))[0]
    job.leased_until = naive_utc() - timedelta(seconds=1)
    await uow.commit()

    second = (await uow.cpu_jobs.claim(limit=1, lease_seconds=60))[0]

    assert second.id == first.id
    assert second.payload == {"value": 1}
    assert second.lease_token != first.lease_token
    assert second.attempt_count == SECOND_ATTEMPT
    assert await uow.cpu_jobs.succeed(first.id, first.lease_token, {"stale": True}) is False
