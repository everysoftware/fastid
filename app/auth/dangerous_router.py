from typing import assert_never, Annotated, Any

from fastapi import APIRouter, Form
from starlette import status

from app.auth.dependencies import (
    AuthDep,
)
from app.auth.exceptions import NoPermission
from app.auth.schemas import UserCreate, UserDTO
from app.authlib.dependencies import auth_backend
from app.authlib.schemas import BearerToken, OAuth2TokenRequest, OAuth2Grant
from app.base.types import UUID

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO
)
async def register(
    service: AuthDep,
    dto: UserCreate,
) -> Any:
    return await service.register(dto)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
)
async def authorize(
    service: AuthDep,
    form: Annotated[OAuth2TokenRequest, Form()],
) -> BearerToken:
    match form.grant_type:
        case OAuth2Grant.password:
            user = await service.authenticate(form)
        case OAuth2Grant.refresh_token:
            assert form.refresh_token is not None
            payload = auth_backend.validate_refresh(form.refresh_token)
            user = await service.get_one(UUID(payload.sub))
        case OAuth2Grant.authorization_code:
            raise NotImplementedError()
        case _:
            assert_never(form.grant_type)
    if "admin" in form.scopes and not user.is_superuser:
        raise NoPermission()
    return auth_backend.create_bearer(user)
