from typing import Annotated, Any

from auth365.schemas import OAuth2Grant, TokenResponse
from fastapi import APIRouter, BackgroundTasks, Depends, Form, status

from app.auth.backend import cookie_transport
from app.auth.dependencies import AuthDep, UserDep
from app.auth.exceptions import NotSupportedGrantError
from app.auth.grants import (
    AuthorizationCodeGrant,
    PasswordGrant,
    RefreshTokenGrant,
)
from app.auth.schemas import (
    OAuth2TokenRequest,
    UserCreate,
    UserDTO,
)
from app.notify.dependencies import NotifyDep
from app.notify.notifications import WelcomeNotification

router = APIRouter(tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO)
async def register(
    service: AuthDep,
    notify: NotifyDep,
    dto: UserCreate,
    background: BackgroundTasks,
) -> Any:
    user = await service.register(dto)
    background.add_task(notify.push, WelcomeNotification(user))
    return user


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def authorize(
    form: Annotated[OAuth2TokenRequest, Form()],
    password_grant: Annotated[PasswordGrant, Depends()],
    authorization_code_grant: Annotated[AuthorizationCodeGrant, Depends()],
    refresh_token_grant: Annotated[RefreshTokenGrant, Depends()],
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            token = await password_grant.authorize(form.as_password_grant())
        case OAuth2Grant.authorization_code:
            token = await authorization_code_grant.authorize(form.as_authorization_code_grant())
        case OAuth2Grant.refresh_token:
            token = await refresh_token_grant.authorize(form.as_refresh_token_grant())
        case _:
            raise NotSupportedGrantError
    return cookie_transport.get_login_response(token)


@router.get("/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK)
def me(user: UserDep) -> Any:
    return user


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    return cookie_transport.get_logout_response()
