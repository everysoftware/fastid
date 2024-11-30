from typing import Any, Annotated

from fastapi import APIRouter, status, Depends, Form

from app.auth.backend import cookie_transport
from app.auth.exceptions import NotSupportedGrant
from app.auth.grants import (
    PasswordGrant,
    AuthorizationCodeGrant,
    RefreshTokenGrant,
)
from app.auth.schemas import (
    OAuth2TokenRequest,
)
from app.authlib.oauth import TokenResponse, OAuth2Grant

router = APIRouter(tags=["Users"])


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
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    return cookie_transport.get_logout_response()
