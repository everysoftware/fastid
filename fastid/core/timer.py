import time
from types import TracebackType
from typing import Self

from fastid.core.dependencies import log


class Timer:
    def __init__(self, name: str, threshold_ms: float = 1.0, slow_ms: float = 10.0) -> None:
        self.name = name
        self.threshold_ms = threshold_ms
        self.slow_ms = slow_ms
        self.start_time: float | None = None
        self.end_time: float | None = None

    def __enter__(self) -> Self:
        self.start_time = time.perf_counter()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        self.end_time = time.perf_counter()
        assert self.start_time is not None
        elapsed_ms = (self.end_time - self.start_time) * 1000

        if elapsed_ms > self.threshold_ms or exc_type is not None:
            status = "ERROR" if exc_type else "SLOW" if elapsed_ms > self.slow_ms else "OK"
            log.warning(f"[PROFILE] {status} | {self.name}: {elapsed_ms:.2f}ms")
