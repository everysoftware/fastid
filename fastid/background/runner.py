import argparse
import asyncio
import signal
from collections.abc import Awaitable, Callable, Iterable
from contextlib import suppress
from typing import Literal, Protocol

from prometheus_client import start_http_server

from fastid.background.config import cpu_worker_settings
from fastid.background.executors import CPUHandlerRegistry, ProcessExecutor
from fastid.background.worker import CPUWorker
from fastid.database.dependencies import engine, get_uow_raw
from fastid.webhooks.config import webhook_settings
from fastid.webhooks.senders.dependencies import client
from fastid.webhooks.worker import WebhookWorker

type QueueName = Literal["webhooks", "cpu"]
type WorkerFactory = Callable[[], "RunnableWorker"]
type AsyncCloser = Callable[[], Awaitable[None]]


class RunnableWorker(Protocol):
    async def run(self) -> None: ...

    def stop(self) -> None: ...


class WorkerRunner:
    def __init__(
        self,
        workers: Iterable[RunnableWorker],
        *,
        closers: Iterable[AsyncCloser] = (),
    ) -> None:
        self.workers = tuple(workers)
        self.closers = tuple(closers)
        self.stopping = False
        self.closed = False

    async def run(self) -> None:
        tasks = tuple(asyncio.create_task(worker.run()) for worker in self.workers)
        try:
            await asyncio.gather(*tasks)
        finally:
            self.stop()
            await asyncio.gather(*tasks, return_exceptions=True)
            await self.aclose()

    def stop(self) -> None:
        if self.stopping:
            return
        self.stopping = True
        for worker in self.workers:
            worker.stop()

    async def aclose(self) -> None:
        if self.closed:
            return
        self.closed = True
        for worker in self.workers:
            closer = getattr(worker, "aclose", None)
            if closer is not None:
                await closer()
        for closer in self.closers:
            await closer()


def normalize_queues(value: str) -> tuple[QueueName, ...]:
    names: list[QueueName] = []
    for raw_name in value.split(","):
        name = raw_name.strip()
        if not name:
            continue
        if name == "webhooks":
            names.append("webhooks")
        elif name == "cpu":
            names.append("cpu")
        else:
            msg = f"Unknown worker queue: {name}"
            raise ValueError(msg)
    if not names:
        msg = "At least one worker queue is required"
        raise ValueError(msg)
    return tuple(dict.fromkeys(names))


def build_runner(
    queues: str,
    *,
    webhook_factory: WorkerFactory,
    cpu_factory: WorkerFactory,
    closers: Iterable[AsyncCloser] = (),
) -> WorkerRunner:
    selected = normalize_queues(queues)
    factories: dict[QueueName, WorkerFactory] = {
        "webhooks": webhook_factory,
        "cpu": cpu_factory,
    }
    return WorkerRunner((factories[name]() for name in selected), closers=closers)


def create_default_runner(queues: str) -> WorkerRunner:
    selected = normalize_queues(queues)
    if "webhooks" in selected and webhook_settings.worker_metrics_port > 0:
        start_http_server(webhook_settings.worker_metrics_port)
    closers: list[AsyncCloser] = [engine.dispose]
    if "webhooks" in selected:
        closers.insert(0, client.aclose)
    return build_runner(
        ",".join(selected),
        webhook_factory=WebhookWorker,
        cpu_factory=lambda: CPUWorker(
            get_uow_raw,
            CPUHandlerRegistry(),
            ProcessExecutor(max_workers=cpu_worker_settings.concurrency),
            cpu_worker_settings,
        ),
        closers=closers,
    )


async def run_selected(queues: str) -> None:
    runner = create_default_runner(queues)
    loop = asyncio.get_running_loop()
    registered_signals: list[signal.Signals] = []
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, runner.stop)
        except NotImplementedError:  # pragma: no cover - Windows uses KeyboardInterrupt cancellation
            continue
        registered_signals.append(signum)
    try:
        await runner.run()
    finally:
        for signum in registered_signals:
            loop.remove_signal_handler(signum)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FastID background worker lanes")
    parser.add_argument("--queues", default="webhooks", help="Comma-separated queues: webhooks,cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with suppress(KeyboardInterrupt):
        asyncio.run(run_selected(args.queues))


if __name__ == "__main__":
    main()
