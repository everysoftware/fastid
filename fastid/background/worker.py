import asyncio
from collections.abc import Callable
from contextlib import suppress
from datetime import timedelta
from typing import Any, Protocol

from fastid.background.config import CPUWorkerSettings
from fastid.background.executors import CPUHandler, CPUHandlerRegistry, UnknownCPUHandlerError
from fastid.background.repositories import ClaimedCPUJob
from fastid.core.dependencies import log_provider
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc

log = log_provider.logger(__name__)

type CPURepositoryFactory = Callable[[], SQLAlchemyUOW]


class CPUExecutor(Protocol):
    async def execute(
        self,
        handler: CPUHandler,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]: ...

    async def aclose(self) -> None: ...


class CPUWorker:
    def __init__(
        self,
        repository_factory: CPURepositoryFactory,
        registry: CPUHandlerRegistry,
        executor: CPUExecutor,
        settings: CPUWorkerSettings,
    ) -> None:
        self.repository_factory = repository_factory
        self.registry = registry
        self.executor = executor
        self.settings = settings
        self.stopping = asyncio.Event()
        self.in_flight: set[asyncio.Task[None]] = set()
        self.closed = False

    async def run(self) -> None:
        log.info("CPU worker started")
        try:
            while not self.stopping.is_set():
                available = self.settings.concurrency - len(self.in_flight)
                if available > 0:
                    jobs = await self._claim(min(self.settings.batch_size, available))
                    for job in jobs:
                        task = asyncio.create_task(self._process_isolated(job))
                        self.in_flight.add(task)
                        task.add_done_callback(self.in_flight.discard)
                if not self.stopping.is_set():
                    await self._wait_for_progress()
        finally:
            await self._drain()
            await self.aclose()
            log.info("CPU worker stopped")

    def stop(self) -> None:
        self.stopping.set()

    async def aclose(self) -> None:
        if self.closed:
            return
        self.closed = True
        await self.executor.aclose()

    async def run_once(self) -> int:
        limit = min(self.settings.batch_size, self.settings.concurrency)
        jobs = await self._claim(limit)
        await asyncio.gather(*(self._process_isolated(job) for job in jobs))
        return len(jobs)

    async def _claim(self, limit: int) -> list[ClaimedCPUJob]:
        async with self.repository_factory() as uow:
            return await uow.cpu_jobs.claim(limit=limit, lease_seconds=self.settings.lease_seconds)
        return []  # pragma: no cover - the unit of work context always enters

    async def _wait_for_progress(self) -> None:
        stop_waiter = asyncio.create_task(self.stopping.wait())
        waiters: set[asyncio.Task[object]] = {stop_waiter}
        waiters.update(self.in_flight)
        try:
            await asyncio.wait(
                waiters,
                timeout=self.settings.poll_seconds,
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            if not stop_waiter.done():
                stop_waiter.cancel()
                with suppress(asyncio.CancelledError):
                    await stop_waiter

    async def _drain(self) -> None:
        pending = set(self.in_flight)
        if not pending:
            return
        _done, pending = await asyncio.wait(pending, timeout=self.settings.drain_timeout_seconds)
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    async def _process_isolated(self, job: ClaimedCPUJob) -> None:
        try:
            await self._process(job)
        except Exception:
            log.exception("Unexpected CPU job processing error: job_id=%s kind=%s", job.id, job.kind)

    async def _process(self, job: ClaimedCPUJob) -> None:
        try:
            handler = self.registry.get(job.kind)
        except UnknownCPUHandlerError as exc:
            await self._fail(job, str(exc))
            return

        ownership_lost = asyncio.Event()
        heartbeat = asyncio.create_task(self._heartbeat(job, ownership_lost))
        execution_error: Exception | None = None
        result: dict[str, Any] | None = None
        try:
            result = await self.executor.execute(handler, job.payload, self.settings.timeout_seconds)
        except Exception as exc:  # noqa: BLE001 - arbitrary handler failures drive durable retry state
            execution_error = exc
        finally:
            heartbeat.cancel()
            with suppress(asyncio.CancelledError):
                await heartbeat

        if ownership_lost.is_set():
            log.warning("Discarding CPU job result after lease loss: job_id=%s kind=%s", job.id, job.kind)
            return
        if execution_error is not None:
            error = f"{type(execution_error).__name__}: {execution_error}"
            if job.attempt_count >= job.max_attempts:
                await self._fail(job, error)
            else:
                await self._retry(job, error)
            return
        assert result is not None
        async with self.repository_factory() as uow:
            await uow.cpu_jobs.succeed(job.id, job.lease_token, result)

    async def _heartbeat(self, job: ClaimedCPUJob, ownership_lost: asyncio.Event) -> None:
        try:
            while True:
                await asyncio.sleep(self.settings.heartbeat_seconds)
                async with self.repository_factory() as uow:
                    owned = await uow.cpu_jobs.heartbeat(job.id, job.lease_token, self.settings.lease_seconds)
                if not owned:
                    ownership_lost.set()
                    return
        except asyncio.CancelledError:
            raise
        except Exception:
            ownership_lost.set()
            log.exception("CPU job heartbeat failed: job_id=%s kind=%s", job.id, job.kind)

    async def _retry(self, job: ClaimedCPUJob, error: str) -> None:
        delays = self.settings.retry_delays_seconds
        delay = delays[min(job.attempt_count - 1, len(delays) - 1)]
        retry_at = naive_utc() + timedelta(seconds=delay)
        async with self.repository_factory() as uow:
            await uow.cpu_jobs.retry(job.id, job.lease_token, error, retry_at)

    async def _fail(self, job: ClaimedCPUJob, error: str) -> None:
        async with self.repository_factory() as uow:
            await uow.cpu_jobs.fail(job.id, job.lease_token, error)
