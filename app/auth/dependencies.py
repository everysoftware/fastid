from typing import Annotated

from auth365.fastapi.transport import CookieTransport, HeaderTransport
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.exceptions import ClientError
from app.auth.config import auth_settings
from app.auth.models import User
from app.auth.service import AuthUseCases
from app.auth.utils import AuthBus

auth_flows = [
    OAuth2PasswordBearer(tokenUrl="auth/token", scheme_name="Password", auto_error=False),
]

AuthDep = Annotated[AuthUseCases, Depends()]

header_transport = HeaderTransport()
cookie_transport = CookieTransport(name="fastidaccesstoken", max_age=auth_settings.jwt_access_expires_in)
verify_token_transport = CookieTransport(
    name="fastidverifytoken",
    scheme_name="VerifyTokenCookie",
    max_age=auth_settings.jwt_verify_token_expires_in,
)
auth_bus = AuthBus(header_transport, cookie_transport)


async def get_user(
    service: AuthDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]


async def get_optional_user(service: AuthDep, request: Request) -> User | None:
    token = auth_bus.parse_request(request, auto_error=False)
    if token is None:
        return None
    try:
        return await service.get_userinfo(token)
    except ClientError:
        return None
