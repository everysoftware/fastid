from typing import Any

from fastapi import APIRouter, Depends
from starlette import status

from app.auth.admin_router import router as admin_auth_router
from app.auth.dangerous_router import router as dangerous_auth_router
from app.auth.fastapi import auth_flows
from app.auth.router import router as auth_router
from app.authlib.dependencies import get_user
from app.base.schemas import ErrorResponse
from app.social.dangerous_router import router as dangerous_social_router
from app.social.router import router as social_router

dangerous_router = APIRouter()
dangerous_router.include_router(dangerous_auth_router)
dangerous_router.include_router(dangerous_social_router)

secure_router = APIRouter(
    dependencies=[Depends(get_user)] + [Depends(f) for f in auth_flows]
)

secure_router.include_router(auth_router)
secure_router.include_router(admin_auth_router)
secure_router.include_router(social_router)

api_router = APIRouter(
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
api_router.include_router(dangerous_router)
api_router.include_router(secure_router)


@api_router.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}


@api_router.get("/exc", include_in_schema=False)
def exc() -> dict[str, Any]:
    raise Exception("test exception")
