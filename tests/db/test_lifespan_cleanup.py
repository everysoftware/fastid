import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import fastid.core.app as app_module
from fastid.core.lifespan import LifespanTasks
from fastid.database.uow import SQLAlchemyUOW
from tests.dependencies import get_test_cache, get_test_uow, test_engine


@pytest.mark.parametrize("failure_at", ["startup", "body"])
async def test_lifespan_disposes_engine_after_failure(failure_at: str, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_async_engine(test_engine.url, pool_size=1, max_overflow=0)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    old_pool = engine.pool
    sender = httpx.AsyncClient()

    async def startup(self: LifespanTasks) -> None:
        await self.healthcheck()
        if failure_at == "startup":
            message = "lifecycle failure"
            raise RuntimeError(message)

    monkeypatch.setattr(app_module, "engine", engine)
    monkeypatch.setattr(app_module, "create_uow", lambda: SQLAlchemyUOW(factory))
    monkeypatch.setattr(app_module, "create_cache", get_test_cache)
    monkeypatch.setattr(LifespanTasks, "on_startup", startup)
    monkeypatch.setattr("fastid.core.lifespan.webhooks_client", sender)
    with pytest.raises(RuntimeError, match="lifecycle failure"):  # noqa: PT012 - exercise context cleanup
        async with app_module.lifespan(FastAPI()):
            message = "lifecycle failure"
            raise RuntimeError(message)
    assert engine.pool is not old_pool
    assert sender.is_closed
    await engine.dispose()


async def test_shutdown_closes_http_client_when_cache_close_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingCacheClient:
        async def aclose(self) -> None:
            message = "cache close failed"
            raise RuntimeError(message)

    tasks = LifespanTasks(uow_factory=get_test_uow, cache_factory=get_test_cache)
    sender = httpx.AsyncClient()
    monkeypatch.setattr(tasks.cache, "client", FailingCacheClient())
    monkeypatch.setattr("fastid.core.lifespan.webhooks_client", sender)
    try:
        with pytest.raises(RuntimeError, match="cache close failed"):
            await tasks.on_shutdown()
        assert sender.is_closed
    finally:
        await sender.aclose()
