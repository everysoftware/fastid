from typing import Any

from fastapi import APIRouter, Depends
from starlette import status

from fastid.admin.router import router as admin_auth_router
from fastid.api.exceptions import TestError
from fastid.apps.router import router as app_router
from fastid.auth.dependencies import auth_flows
from fastid.auth.router import router as auth_router
from fastid.core.schemas import ErrorResponse
from fastid.notify.router import router as notifier_router
from fastid.oauth.router import router as oauth_router
from fastid.profile.router import router as profile_router

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
secured_router.include_router(notifier_router)
secured_router.include_router(profile_router)
secured_router.include_router(admin_auth_router)
secured_router.include_router(app_router)

api_router.include_router(secured_router)


@api_router.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}


@api_router.get("/exc", include_in_schema=False)
def exc() -> dict[str, Any]:
    raise TestError
