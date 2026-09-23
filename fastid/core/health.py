from typing import Any

from fastapi import APIRouter

from fastid.cache.dependencies import CacheDep
from fastid.database.dependencies import UOWDep

health_router = APIRouter()


@health_router.get("/readiness")
async def readiness() -> dict[str, Any]:  # pragma: nocover
    return {"status": "ok"}


@health_router.get("/liveness")
async def liveness(uow: UOWDep, cache: CacheDep) -> dict[str, Any]:  # pragma: nocover
    response = {"db": True, "cache": True}
    try:
        await uow.healthcheck()
    except Exception:  # noqa: BLE001
        response["db"] = False
    try:
        await cache.healthcheck()
    except Exception:  # noqa: BLE001
        response["cache"] = False
    return response
