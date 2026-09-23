import asyncio
import os
import time

import pytest

from fastid.background.executors import (
    CPUExecutionError,
    CPUExecutionTimeoutError,
    CPUHandlerRegistry,
    ProcessExecutor,
    UnknownCPUHandlerError,
)
from tests.background.handlers import bounded_cpu, process_id, raises_error, sleeps


def test_registry_resolves_trusted_handlers_and_rejects_duplicates_or_unknown_kinds() -> None:
    registry = CPUHandlerRegistry([("pid", process_id)])

    assert registry.get("pid") is process_id
    with pytest.raises(ValueError, match="Duplicate CPU handler kind: pid"):
        CPUHandlerRegistry([("pid", process_id), ("pid", bounded_cpu)])
    with pytest.raises(UnknownCPUHandlerError, match="Unknown CPU handler kind: missing"):
        registry.get("missing")


async def test_executor_runs_handler_in_a_child_process() -> None:
    executor = ProcessExecutor(max_workers=1)
    try:
        result = await executor.execute(process_id, {}, timeout_seconds=5)
    finally:
        await executor.aclose()

    assert result["pid"] != os.getpid()


async def test_executor_keeps_event_loop_responsive_during_cpu_work() -> None:
    executor = ProcessExecutor(max_workers=1)
    ticked = asyncio.Event()

    async def tick() -> None:
        await asyncio.sleep(0.02)
        ticked.set()

    execution = asyncio.create_task(executor.execute(bounded_cpu, {"duration": 0.3}, timeout_seconds=5))
    ticker = asyncio.create_task(tick())
    try:
        await asyncio.wait_for(ticked.wait(), timeout=1)
        assert execution.done() is False
        assert "value" in await execution
        await ticker
    finally:
        await executor.aclose()


async def test_executor_preserves_handler_error_context() -> None:
    executor = ProcessExecutor(max_workers=1)
    try:
        with pytest.raises(CPUExecutionError, match="ValueError: handler exploded") as exc_info:
            await executor.execute(raises_error, {}, timeout_seconds=5)
    finally:
        await executor.aclose()

    assert isinstance(exc_info.value.__cause__, ValueError)


async def test_executor_enforces_timeout() -> None:
    executor = ProcessExecutor(max_workers=1)
    try:
        with pytest.raises(CPUExecutionTimeoutError, match="0.05 seconds"):
            await executor.execute(sleeps, {"seconds": 0.3}, timeout_seconds=0.05)
    finally:
        await executor.aclose()


async def test_executor_close_terminates_running_timed_out_work() -> None:
    executor = ProcessExecutor(max_workers=1)
    await executor.execute(process_id, {}, timeout_seconds=5)
    started = time.monotonic()

    with pytest.raises(CPUExecutionTimeoutError):
        await executor.execute(sleeps, {"seconds": 2}, timeout_seconds=0.05)
    await executor.aclose()

    assert time.monotonic() - started < 1
