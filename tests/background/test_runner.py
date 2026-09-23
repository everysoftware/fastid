import asyncio

import pytest

from fastid.background.runner import WorkerRunner, build_runner, normalize_queues


class FakeWorker:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.stopped = asyncio.Event()
        self.stop_calls = 0

    async def run(self) -> None:
        self.started.set()
        await self.stopped.wait()

    def stop(self) -> None:
        self.stop_calls += 1
        self.stopped.set()


def test_normalize_queues_deduplicates_names_in_input_order() -> None:
    assert normalize_queues("webhooks,cpu,webhooks") == ("webhooks", "cpu")


def test_build_runner_constructs_only_selected_workers() -> None:
    webhook_worker = FakeWorker()
    cpu_worker = FakeWorker()
    webhook_calls = 0
    cpu_calls = 0

    def webhook_factory() -> FakeWorker:
        nonlocal webhook_calls
        webhook_calls += 1
        return webhook_worker

    def cpu_factory() -> FakeWorker:
        nonlocal cpu_calls
        cpu_calls += 1
        return cpu_worker

    runner = build_runner("webhooks,webhooks", webhook_factory=webhook_factory, cpu_factory=cpu_factory)

    assert runner.workers == (webhook_worker,)
    assert webhook_calls == 1
    assert cpu_calls == 0


def test_unknown_queue_is_rejected_before_worker_construction() -> None:
    factory_calls = 0

    def factory() -> FakeWorker:
        nonlocal factory_calls
        factory_calls += 1
        return FakeWorker()

    with pytest.raises(ValueError, match="Unknown worker queue: maintenance"):
        build_runner("webhooks,maintenance", webhook_factory=factory, cpu_factory=factory)

    assert factory_calls == 0


async def test_runner_stops_every_worker_and_closes_resources_once() -> None:
    workers = (FakeWorker(), FakeWorker())
    close_calls = 0

    async def close_resource() -> None:
        nonlocal close_calls
        close_calls += 1

    runner = WorkerRunner(workers, closers=(close_resource,))
    running = asyncio.create_task(runner.run())
    await asyncio.gather(*(worker.started.wait() for worker in workers))

    runner.stop()
    await asyncio.wait_for(running, timeout=1)
    await runner.aclose()

    assert [worker.stop_calls for worker in workers] == [1, 1]
    assert close_calls == 1
