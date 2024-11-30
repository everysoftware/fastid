from typing import Any, Annotated
from fastapi import APIRouter, status, Depends, Form

from app.auth.dependencies import UserManagerDep, UserDep
from app.auth.exceptions import NotSupportedGrant
from app.auth.grants import (
    PasswordGrant,
    AuthorizationCodeGrant,
    RefreshTokenGrant,
)
from app.auth.permissions import Requires
from app.auth.schemas import (
    UserDTO,
    UserUpdate,
    UserCreate,
    OAuth2TokenRequest,
    UserChangeEmail,
    UserChangePassword,
)
from app.authlib.dependencies import cookie_transport
from app.authlib.oauth import TokenResponse, OAuth2Grant

router = APIRouter(tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO
)
async def register(
    service: Annotated[UserManagerDep, Depends()],
    dto: UserCreate,
) -> Any:
    return await service.register(dto)


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
            token = await authorization_code_grant.authorize(
                form.as_authorization_code_grant()
            )
        case OAuth2Grant.refresh_token:
            token = await refresh_token_grant.authorize(
                form.as_refresh_token_grant()
            )
        case _:
            raise NotSupportedGrant()
    return cookie_transport.get_login_response(token)


@router.get(
    "/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK
)
def me(user: UserDep) -> Any:
    return user


@router.patch(
    "/users/me/profile", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def patch(
    service: UserManagerDep,
    user: UserDep,
    dto: UserUpdate,
) -> Any:
    return await service.update_profile(user, dto)


@router.patch(
    "/users/me/email",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_email(
    service: UserManagerDep, user: UserDep, dto: UserChangeEmail
) -> Any:
    return await service.change_email(user, dto)


@router.patch(
    "/users/me/password",
    dependencies=[Depends(Requires(action_verified=True))],
    response_model=UserDTO,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    service: UserManagerDep, user: UserDep, dto: UserChangePassword
) -> Any:
    return await service.change_password(user, dto)


@router.delete(
    "/users/me", response_model=UserDTO, status_code=status.HTTP_200_OK
)
async def delete(service: UserManagerDep, user: UserDep) -> Any:
    return await service.delete_account(user)


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    return cookie_transport.get_logout_response()
