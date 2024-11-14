from typing import Any

from fastapi import APIRouter, Depends
from starlette import status

from app.auth.admin_router import router as admin_auth_router
from app.auth.fastapi import auth_flows
from app.auth.router import router as auth_router
from app.base.schemas import ErrorResponse
from app.oauth.accounts_router import router as oauth_accounts_router
from app.oauth.login_router import router as oauth_router
from app.public.router import router as external_router

api_router = APIRouter(
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

api_router.include_router(external_router)

private_router = APIRouter(dependencies=[Depends(f) for f in auth_flows])
private_router.include_router(auth_router)
private_router.include_router(oauth_router)
private_router.include_router(admin_auth_router)
private_router.include_router(oauth_accounts_router)

api_router.include_router(private_router)


@api_router.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}


@api_router.get("/exc", include_in_schema=False)
def exc() -> dict[str, Any]:
    raise Exception("test exception")