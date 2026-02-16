from typing import Any

from fastapi import APIRouter, Depends
from starlette import status

from fastid.api.exceptions import TestError
from fastid.apps.router import router as app_router
from fastid.auth.dependencies import auth_flows
from fastid.auth.router import router as auth_router
from fastid.cache.dependencies import CacheDep
from fastid.core.schemas import ErrorResponse
from fastid.database.dependencies import UOWDep
from fastid.notify.router import router as notify_router
from fastid.oauth.router import router as oauth_router
from fastid.profile.router import router as profile_router
from fastid.superuser.router import router as superuser_router

api_router = APIRouter(
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

secured_router = APIRouter(dependencies=[Depends(f) for f in auth_flows])
secured_router.include_router(auth_router)
secured_router.include_router(oauth_router)
secured_router.include_router(notify_router)
secured_router.include_router(profile_router)
secured_router.include_router(superuser_router)
secured_router.include_router(app_router)

api_router.include_router(secured_router)


@api_router.get("/readiness", include_in_schema=False)
async def readiness() -> dict[str, Any]:  # pragma: nocover
    return {"status": "ok"}


@api_router.get("/liveness", include_in_schema=False)
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


@api_router.get("/exc", include_in_schema=False)
def exc() -> dict[str, Any]:
    raise TestError
