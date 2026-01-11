import json
from abc import ABC, abstractmethod
from typing import Any, cast

from redis.asyncio import Redis

from fastid.cache.exceptions import KeyNotFoundError


class CacheStorage(ABC):
    client: Any

    @abstractmethod
    async def keys(self, pattern: str = "*") -> set[str]: ...

    @abstractmethod
    async def set(self, key: str, value: Any, *, expire: int | None = None) -> str: ...

    @abstractmethod
    async def get(self, key: str) -> str: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def pop(self, key: str) -> str: ...

    @abstractmethod
    async def healthcheck(self) -> None: ...


class RedisStorage(CacheStorage):
    key: str
    client: Redis

    def __init__(self, redis: Redis, *, key: str = "fastapi") -> None:
        self.client = redis
        self.key = key

    async def keys(self, pattern: str = "*") -> set[str]:
        keys = await self.client.keys(f"{self.key}:{pattern}")
        return {key.decode().split(":")[-1] for key in keys}

    async def set(self, key: str, value: Any, *, expire: int | None = None) -> str:
        json_str = json.dumps(value, ensure_ascii=True)
        await self.client.set(f"{self.key}:{key}", json_str, ex=expire)
        return json_str

    async def get(self, key: str) -> str:
        value = await self.client.get(f"{self.key}:{key}")
        if value is None:
            raise KeyNotFoundError(f"Key {key} not found")
        return str(json.loads(value))

    async def delete(self, key: str) -> None:
        await self.client.delete(f"{self.key}:{key}")

    async def pop(self, key: str) -> str:
        value = await self.client.getdel(f"{self.key}:{key}")
        if value is None:
            raise KeyNotFoundError(f"Key {key} not found")
        return cast(str, json.loads(value))

    async def healthcheck(self) -> None:
        await self.client.ping()
