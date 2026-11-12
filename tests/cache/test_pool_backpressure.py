import asyncio
import time

import pytest
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from fastid.cache.dependencies import pool as application_pool
from tests.config import test_settings

MINIMUM_WAIT_SECONDS = 0.05


@pytest.mark.parametrize("outcome", ["release", "timeout", "cancel"])
async def test_saturated_application_pool(outcome: str) -> None:
    # Exercise the application's chosen pool policy against the isolated test
    # Redis, with one connection held to deterministically exhaust the budget.
    pool = type(application_pool).from_url(test_settings.redis_url, max_connections=1)
    pool.timeout = 0.15
    client = Redis(connection_pool=pool)
    held = await pool.get_connection()
    started = asyncio.Event()

    async def ping() -> bool:
        started.set()
        return await client.ping()

    task = asyncio.create_task(ping())
    try:
        await started.wait()
        assert not task.done(), "Pool must wait instead of rejecting healthy concurrent traffic"
        if outcome == "release":
            await pool.release(held)
            held = None
            assert await asyncio.wait_for(task, timeout=1)
        elif outcome == "timeout":
            start = time.monotonic()
            with pytest.raises(RedisConnectionError, match="No connection available"):
                await asyncio.wait_for(task, timeout=1)
            assert time.monotonic() - start >= MINIMUM_WAIT_SECONDS
        else:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        if held is not None:
            await pool.release(held)
            held = None
        assert await client.ping()
    finally:
        if held is not None:
            await pool.release(held)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await client.aclose()
        await pool.aclose()


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), None])
def test_pool_wait_requires_finite_positive_timeout(timeout: float | None) -> None:
    from pydantic import ValidationError

    from fastid.cache.config import RedisSettings

    with pytest.raises(ValidationError):
        RedisSettings(_env_file=None, pool_timeout=timeout)
