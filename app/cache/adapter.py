import json
from typing import Any, Literal, TypeVar, overload
from typing import cast as _cast

from redis.asyncio import Redis

from app.cache.exceptions import KeyNotFoundError

T = TypeVar("T")


class CacheAdapter:
    client: Redis
    key: str

    def __init__(self, redis: Redis, *, key: str = "fastapi"):
        self.client = redis
        self.key = key

    async def keys(self, pattern: str) -> set[str]:
        keys = await self.client.keys(f"{self.key}:{pattern}")
        return set(keys)

    async def set(self, key: str, value: Any, expire: int | None = None) -> str:
        json_str = json.dumps(value, ensure_ascii=True)
        await self.client.set(f"{self.key}:{key}", json_str, ex=expire)
        return json_str

    @overload
    async def get(
        self,
        key: str,
        cast: Literal[None] = None,
    ) -> Any: ...

    @overload
    async def get(
        self,
        key: str,
        cast: type[T],
    ) -> T: ...

    async def get(
        self,
        key: str,
        cast: type[T] | None = None,
    ) -> Any | T:
        value = await self.client.get(f"{self.key}:{key}")
        if value is None:
            raise KeyNotFoundError(f"Key {key} not found")
        if cast is None:
            return value
        return _cast(cast, json.loads(value))  # type: ignore[valid-type]

    async def delete(self, key: str) -> Any:
        return await self.client.delete(f"{self.key}:{key}")

    @overload
    async def pop[T](
        self,
        key: str,
        cast: Literal[None] = None,
    ) -> Any: ...

    @overload
    async def pop[T](
        self,
        key: str,
        cast: type[T],
    ) -> T | None: ...

    async def pop(self, key: str, cast: type[T] | None = None) -> Any | T:
        value = await self.get(key, cast)
        await self.delete(key)
        return value
