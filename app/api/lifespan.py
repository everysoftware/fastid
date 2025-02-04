from typing import Self, Any

from app.cache.dependencies import redis_client


class LifespanTasks:
    def __init__(self) -> None:
        self.redis = redis_client

    async def on_startup(self) -> None:
        await self.healthcheck()

    async def on_shutdown(self) -> None:
        await self.redis.aclose()

    async def healthcheck(self) -> None:
        await self.redis.ping()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass
