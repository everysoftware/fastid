from abc import ABC, abstractmethod
from typing import Any, cast

import orjson
from redis.asyncio import Redis

from fastid.cache.exceptions import KeyNotFoundError
from fastid.cache.locks import DistributedLock


class CacheStorage(ABC):
    client: Any

    @abstractmethod
    async def keys(self, pattern: str = "*") -> set[str]: ...

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        *,
        expire: int | None = None,
        lock: DistributedLock | None = None,
    ) -> str: ...

    @abstractmethod
    async def get(self, key: str) -> str: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def pop(self, key: str) -> str: ...

    @abstractmethod
    async def healthcheck(self) -> None: ...

    @abstractmethod
    def lock(self, name: str, **kwargs: Any) -> DistributedLock: ...


class RedisStorage(CacheStorage):
    key: str
    client: Redis

    def __init__(self, redis: Redis, *, key: str = "fastapi") -> None:
        self.client = redis
        self.key = key

    async def keys(self, pattern: str = "*") -> set[str]:
        keys = await self.client.keys(f"{self.key}:{pattern}")
        return {key.decode().split(":")[-1] for key in keys}

    async def set(
        self,
        key: str,
        value: Any,
        *,
        expire: int | None = None,
        lock: DistributedLock | None = None,
    ) -> str:
        json_str = orjson.dumps(value).decode()
        if expire == 0:
            return json_str
        if lock is None:
            await self.client.set(f"{self.key}:{key}", json_str, ex=expire)
        else:
            await lock.set_if_owned(f"{self.key}:{key}", json_str, expire)
        return json_str

    async def get(self, key: str) -> Any:
        value = await self.client.get(f"{self.key}:{key}")
        if value is None:
            msg = f"Key {key} not found"
            raise KeyNotFoundError(msg)
        return orjson.loads(value)

    async def delete(self, key: str) -> None:
        await self.client.delete(f"{self.key}:{key}")

    async def invalidate(self, key: str) -> None:
        # Revoking an in-flight fill is essential even if its original lease
        # expired and another reader acquired it before the DB commit.
        async with self.client.pipeline(transaction=True) as pipeline:
            pipeline.delete(f"{self.key}:{key}")
            pipeline.delete(f"lock:{key}")
            await pipeline.execute()

    async def pop(self, key: str) -> str:
        value = await self.client.getdel(f"{self.key}:{key}")
        if value is None:
            msg = f"Key {key} not found"
            raise KeyNotFoundError(msg)
        return cast(str, orjson.loads(value))

    async def healthcheck(self) -> None:
        await self.client.ping()

    def lock(self, name: str, **kwargs: Any) -> DistributedLock:
        return DistributedLock(self.client, name, **kwargs)
