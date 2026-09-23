import asyncio
from typing import Any

import pytest

from fastid.background.config import CPUWorkerSettings
from fastid.background.executors import CPUHandler, CPUHandlerRegistry
from fastid.background.models import CPUJob
from fastid.background.repositories import CPUJobRepository
from fastid.background.worker import CPUWorker
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc, uuid
from tests.background.handlers import raises_error
from tests.dependencies import get_test_uow

TWO_JOBS = 2


def echo(payload: dict[str, Any]) -> dict[str, Any]:
    return {"value": payload["value"]}


class DirectExecutor:
    def __init__(self) -> None:
        self.closed = False

    async def execute(
        self,
        handler: CPUHandler,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        del timeout_seconds
        return handler(payload)

    async def aclose(self) -> None:
        self.closed = True


class ControlledExecutor(DirectExecutor):
    def __init__(self) -> None:
        super().__init__()
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def execute(
        self,
        handler: CPUHandler,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        del timeout_seconds
        self.started.set()
        await self.release.wait()
        return handler(payload)


def worker_settings(**overrides: Any) -> CPUWorkerSettings:
    values: dict[str, Any] = {
        "concurrency": 2,
        "batch_size": 10,
        "poll_seconds": 0.01,
        "lease_seconds": 5,
        "heartbeat_seconds": 1,
        "timeout_seconds": 5,
        "drain_timeout_seconds": 1,
        "retry_delays_seconds": (0,),
    }
    values.update(overrides)
    return CPUWorkerSettings(**values)


def test_worker_settings_require_heartbeat_shorter_than_lease() -> None:
    with pytest.raises(ValueError, match="heartbeat_seconds must be shorter than lease_seconds"):
        worker_settings(lease_seconds=1, heartbeat_seconds=1)


async def test_run_once_isolates_handler_errors_and_retries_until_max_attempts(uow: SQLAlchemyUOW) -> None:
    success = CPUJob(kind="echo", payload={"value": 42}, next_attempt_at=naive_utc())
    failure = CPUJob(kind="raises", payload={}, max_attempts=TWO_JOBS, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(success)
    await uow.cpu_jobs.add(failure)
    await uow.commit()
    worker = CPUWorker(
        get_test_uow,
        CPUHandlerRegistry({"echo": echo, "raises": raises_error}),
        DirectExecutor(),
        worker_settings(),
    )

    assert await worker.run_once() == TWO_JOBS
    await uow.session.refresh(success)
    await uow.session.refresh(failure)
    assert success.status == "succeeded"
    assert success.result == {"value": 42}
    assert failure.status == "pending"
    assert failure.attempt_count == 1
    assert "ValueError: handler exploded" in (failure.error or "")

    assert await worker.run_once() == 1
    await uow.session.refresh(failure)
    assert failure.status == "failed"
    assert failure.attempt_count == TWO_JOBS
    assert failure.completed_at is not None


async def test_unknown_handler_kind_is_a_terminal_failure(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="unregistered", payload={}, max_attempts=3, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    await uow.commit()
    worker = CPUWorker(get_test_uow, CPUHandlerRegistry(), DirectExecutor(), worker_settings())

    assert await worker.run_once() == 1

    await uow.session.refresh(job)
    assert job.status == "failed"
    assert job.attempt_count == 1
    assert job.error == "Unknown CPU handler kind: unregistered"


async def test_heartbeat_keeps_a_long_running_job_owned(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="echo", payload={"value": 7}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    await uow.commit()
    executor = ControlledExecutor()
    worker = CPUWorker(
        get_test_uow,
        CPUHandlerRegistry({"echo": echo}),
        executor,
        worker_settings(concurrency=1, lease_seconds=1, heartbeat_seconds=0.1),
    )
    running = asyncio.create_task(worker.run_once())
    await asyncio.wait_for(executor.started.wait(), timeout=1)

    try:
        await asyncio.sleep(1.2)
        async with get_test_uow() as competing_uow:
            reclaimed = await competing_uow.cpu_jobs.claim(limit=1, lease_seconds=1)
        assert reclaimed == []
    finally:
        executor.release.set()
        await running

    await uow.session.refresh(job)
    assert job.status == "succeeded"


async def test_lost_heartbeat_discards_eventual_handler_result(
    uow: SQLAlchemyUOW,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = CPUJob(kind="echo", payload={"value": 9}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    await uow.commit()
    executor = ControlledExecutor()
    worker = CPUWorker(
        get_test_uow,
        CPUHandlerRegistry({"echo": echo}),
        executor,
        worker_settings(concurrency=1, lease_seconds=1, heartbeat_seconds=0.05),
    )
    succeed_called = False
    original_succeed = CPUJobRepository.succeed

    async def tracked_succeed(repository: CPUJobRepository, *args: Any, **kwargs: Any) -> bool:
        nonlocal succeed_called
        succeed_called = True
        return await original_succeed(repository, *args, **kwargs)

    monkeypatch.setattr(CPUJobRepository, "succeed", tracked_succeed)
    running = asyncio.create_task(worker.run_once())
    await asyncio.wait_for(executor.started.wait(), timeout=1)
    replacement_token = uuid()
    async with get_test_uow() as owner_uow:
        owned_job = await owner_uow.cpu_jobs.get(job.id)
        owned_job.lease_token = replacement_token

    try:
        await asyncio.sleep(0.15)
    finally:
        executor.release.set()
        await running

    await uow.session.refresh(job)
    assert succeed_called is False
    assert job.status == "processing"
    assert job.lease_token == replacement_token
    assert job.result is None


async def test_stop_prevents_claiming_another_job_and_drains_current_work(uow: SQLAlchemyUOW) -> None:
    first = CPUJob(kind="echo", payload={"value": 1}, priority=10, next_attempt_at=naive_utc())
    second = CPUJob(kind="echo", payload={"value": 2}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(first)
    await uow.cpu_jobs.add(second)
    await uow.commit()
    executor = ControlledExecutor()
    worker = CPUWorker(
        get_test_uow,
        CPUHandlerRegistry({"echo": echo}),
        executor,
        worker_settings(concurrency=1, batch_size=1, drain_timeout_seconds=1),
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(executor.started.wait(), timeout=1)

    worker.stop()
    executor.release.set()
    await asyncio.wait_for(running, timeout=1)

    await uow.session.refresh(first)
    await uow.session.refresh(second)
    assert first.status == "succeeded"
    assert second.status == "pending"
    assert second.attempt_count == 0
    assert executor.closed is True


async def test_drain_timeout_leaves_job_recoverable_after_lease_expiry(uow: SQLAlchemyUOW) -> None:
    job = CPUJob(kind="echo", payload={"value": 3}, next_attempt_at=naive_utc())
    await uow.cpu_jobs.add(job)
    await uow.commit()
    executor = ControlledExecutor()
    worker = CPUWorker(
        get_test_uow,
        CPUHandlerRegistry({"echo": echo}),
        executor,
        worker_settings(
            concurrency=1,
            batch_size=1,
            lease_seconds=1,
            heartbeat_seconds=0.1,
            drain_timeout_seconds=0.05,
        ),
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(executor.started.wait(), timeout=1)

    worker.stop()
    await asyncio.wait_for(running, timeout=1)

    await uow.session.refresh(job)
    assert job.status == "processing"
    assert executor.closed is True
    await asyncio.sleep(1.1)
    async with get_test_uow() as recovering_uow:
        reclaimed = await recovering_uow.cpu_jobs.claim(limit=1, lease_seconds=1)
    assert [claim.id for claim in reclaimed] == [job.id]
