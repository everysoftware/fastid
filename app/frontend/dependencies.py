from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from app.api.exceptions import Unauthorized, ClientError
from app.auth.dependencies import UserManagerDep
from app.auth.grants import AuthorizationCodeGrant
from app.auth.models import User
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.dependencies import cookie_transport


async def get_user(auth: UserManagerDep, request: Request) -> User | None:
    token = cookie_transport.get_token(request)
    if token is None:
        return None
    try:
        return await auth.get_userinfo(token)
    except ClientError:
        return None


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
