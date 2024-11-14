from typing import Any, Annotated

from fastapi import APIRouter, Form
from starlette import status

from app.auth.dependencies import UserDep, AuthDep
from app.auth.schemas import UserDTO, OAuth2TokenRequest
from app.authlib.schemas import TokenResponse

router = APIRouter(prefix="/public", tags=["Public API"])


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
)
async def authorize(
    service: AuthDep,
    form: Annotated[OAuth2TokenRequest, Form()],
) -> TokenResponse:
    return await service.authorize(form)


@router.get(
    "/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK
)
def me(user: UserDep) -> Any:
    return user
