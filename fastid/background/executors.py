import asyncio
import multiprocessing
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ProcessPoolExecutor
from typing import Any

type CPUHandler = Callable[[dict[str, Any]], dict[str, Any]]


def _terminate_pool(pool: ProcessPoolExecutor) -> None:
    processes = tuple(pool._processes.values())  # noqa: SLF001 - no public termination API before Python 3.14
    pool.shutdown(wait=False, cancel_futures=True)
    for process in processes:
        if process.is_alive():
            process.terminate()
    for process in processes:
        process.join(timeout=1)


class UnknownCPUHandlerError(LookupError):
    pass


class CPUExecutionError(RuntimeError):
    pass


class CPUExecutionTimeoutError(TimeoutError):
    pass


class CPUHandlerRegistry:
    def __init__(
        self,
        handlers: Mapping[str, CPUHandler] | Iterable[tuple[str, CPUHandler]] = (),
    ) -> None:
        entries = handlers.items() if isinstance(handlers, Mapping) else handlers
        self._handlers: dict[str, CPUHandler] = {}
        for kind, handler in entries:
            if kind in self._handlers:
                msg = f"Duplicate CPU handler kind: {kind}"
                raise ValueError(msg)
            self._handlers[kind] = handler

    def get(self, kind: str) -> CPUHandler:
        try:
            return self._handlers[kind]
        except KeyError as exc:
            msg = f"Unknown CPU handler kind: {kind}"
            raise UnknownCPUHandlerError(msg) from exc


class ProcessExecutor:
    def __init__(self, max_workers: int = 1) -> None:
        self._pool: ProcessPoolExecutor | None = ProcessPoolExecutor(
            max_workers=max_workers,
            mp_context=multiprocessing.get_context("spawn"),
        )

    async def execute(
        self,
        handler: CPUHandler,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        if self._pool is None:
            msg = "Process executor is closed"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(self._pool, handler, payload)
        try:
            return await asyncio.wait_for(future, timeout=timeout_seconds)
        except TimeoutError as exc:
            msg = f"CPU handler exceeded timeout of {timeout_seconds} seconds"
            raise CPUExecutionTimeoutError(msg) from exc
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
            raise CPUExecutionError(msg) from exc

    async def aclose(self) -> None:
        pool = self._pool
        if pool is None:
            return
        self._pool = None
        await asyncio.to_thread(_terminate_pool, pool)
