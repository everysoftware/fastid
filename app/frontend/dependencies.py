from typing import Annotated

from auth365.exceptions import Auth365Error
from fastapi import Depends
from starlette.requests import Request

from app.api.exceptions import ClientError, UnauthorizedError
from app.auth.backend import (
    cookie_transport,
    token_backend,
    verify_token_transport,
)
from app.auth.dependencies import AuthDep
from app.auth.grants import AuthorizationCodeGrant
from app.auth.models import User
from app.auth.schemas import OAuth2ConsentRequest


async def get_optional_user(
    auth: AuthDep,
    request: Request,
) -> User | None:
    token = cookie_transport.get_token(request)
    if token is None:
        return None
    try:
        return await auth.get_userinfo(token)
    except ClientError:
        return None


async def get_user(
    auth: AuthDep,
    request: Request,
) -> User:
    token = cookie_transport.get_token(request)
    if token is None:
        raise UnauthorizedError()
    try:
        return await auth.get_userinfo(token)
    except ClientError as e:
        raise UnauthorizedError() from e


def action_verified(
    request: Request,
) -> bool:
    token = verify_token_transport.get_token(request)
    if token is None:
        return False
    try:
        token_backend.validate("verify", token)
    except Auth365Error:
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
            raise UnauthorizedError()
        else:
            consent = OAuth2ConsentRequest.model_validate(consent_data)
    return await authorization_code_grant.validate_consent(consent)
