from typing import Any

from prometheus_client import multiprocess


def child_exit(server: Any, worker: Any) -> None:  # noqa: ARG001
    multiprocess.mark_process_dead(worker.pid)  # type: ignore[no-untyped-call]
