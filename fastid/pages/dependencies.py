from typing import Annotated

from fastapi import Depends
from fastlink.exceptions import FastLinkError
from starlette.requests import Request

from fastid.api.exceptions import ClientError, UnauthorizedError
from fastid.auth.dependencies import AuthDep, cookie_transport, verify_token_transport
from fastid.auth.grants import AuthorizationCodeGrant
from fastid.auth.models import User
from fastid.auth.schemas import OAuth2ConsentRequest
from fastid.security.jwt import (
    jwt_backend,
)


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
        raise UnauthorizedError
    try:
        return await auth.get_userinfo(token)
    except ClientError as e:
        raise UnauthorizedError from e


def action_verified(
    request: Request,
) -> bool:
    token = verify_token_transport.get_token(request)
    if token is None:
        return False
    try:
        jwt_backend.validate("verify", token)
    except FastLinkError:
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
            raise UnauthorizedError
        consent = OAuth2ConsentRequest.model_validate(consent_data)
    return await authorization_code_grant.validate_consent(consent)
