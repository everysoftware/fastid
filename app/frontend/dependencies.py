from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from app.api.exceptions import Unauthorized, ClientError
from app.auth.dependencies import UserManagerDep
from app.auth.grants import AuthorizationCodeGrant
from app.auth.models import User
from app.auth.schemas import OAuth2ConsentRequest
from app.auth.backend import (
    cookie_transport,
    verify_token_transport,
    token_backend,
)


async def get_user(
    auth: UserManagerDep,
    token: Annotated[str | None, Depends(cookie_transport)],
) -> User | None:
    if token is None:
        return None
    try:
        return await auth.get_userinfo(token)
    except ClientError:
        return None


async def get_one_user(
    auth: UserManagerDep,
    token: Annotated[str | None, Depends(cookie_transport)],
) -> User:
    if token is None:
        raise Unauthorized()
    try:
        return await auth.get_userinfo(token)
    except ClientError:
        raise Unauthorized() from None


def action_verified(
    token: Annotated[str | None, Depends(verify_token_transport)],
) -> bool:
    if token is None:
        return False
    try:
        token_backend.validate_custom("verify", token)
    except ClientError:
        return False
    return True


async def valid_consent(
    request: Request,
    consent: Annotated[OAuth2ConsentRequest, Depends()],
    authorization_code_grant: Annotated[AuthorizationCodeGrant, Depends()],
) -> OAuth2ConsentRequest:
    if not request.query_params:
        consent_data = request.session.get("consent")
        if consent_data is None:
            raise Unauthorized()
        else:
            consent = OAuth2ConsentRequest.model_validate(consent_data)
    return await authorization_code_grant.validate_consent(consent)
