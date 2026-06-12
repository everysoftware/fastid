import asyncio
import uuid
from types import TracebackType
from typing import Self

from redis.asyncio import Redis

from fastid.cache.exceptions import LockError

UNLOCK_SCRIPT = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """


class DistributedLock:
    def __init__(
        self,
        redis: Redis,
        name: str,
        *,
        timeout: int = 30,
        blocking: bool = False,
        blocking_timeout: float | None = None,
    ) -> None:
        self._redis = redis
        self._name = f"lock:{name}"
        self._lock_timeout = timeout
        self._blocking = blocking
        self._blocking_timeout = blocking_timeout
        self._token: str = ""
        self._unlock_script = self._redis.register_script(UNLOCK_SCRIPT)

    async def acquire(self) -> bool:
        self._token = str(uuid.uuid4())
        if self._blocking:
            deadline = None
            if self._blocking_timeout is not None:
                deadline = asyncio.get_event_loop().time() + self._blocking_timeout
            while True:
                acquired = await self._redis.set(
                    self._name,
                    self._token,
                    nx=True,
                    ex=self._lock_timeout,
                )
                if acquired:
                    return True
                if deadline and asyncio.get_event_loop().time() >= deadline:
                    return False
                await asyncio.sleep(0.1)
        else:
            return bool(
                await self._redis.set(
                    self._name,
                    self._token,
                    nx=True,
                    ex=self._lock_timeout,
                )
            )

    async def release(self) -> None:
        if not self._token:
            return
        await self._unlock_script(keys=[self._name], args=[self._token])
        self._token = ""

    async def __aenter__(self) -> Self:
        if not await self.acquire():
            msg = f"Could not acquire lock '{self._name}'"
            raise LockError(msg)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        await self.release()
        return False
