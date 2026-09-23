import os
import time
from typing import Any


def process_id(_payload: dict[str, Any]) -> dict[str, Any]:
    return {"pid": os.getpid()}


def bounded_cpu(payload: dict[str, Any]) -> dict[str, Any]:
    duration = float(payload["duration"])
    started = time.process_time()
    value = 0
    while time.process_time() - started < duration:
        value = (value * 33 + 17) % 1_000_003
    return {"value": value}


def raises_error(_payload: dict[str, Any]) -> dict[str, Any]:
    msg = "handler exploded"
    raise ValueError(msg)


def sleeps(payload: dict[str, Any]) -> dict[str, Any]:
    time.sleep(float(payload["seconds"]))
    return {"finished": True}
