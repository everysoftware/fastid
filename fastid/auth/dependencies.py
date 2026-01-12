from collections.abc import Callable, Iterable
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import APIKeyCookie, APIKeyHeader, OAuth2PasswordBearer
from fastlink.integrations.fastapi.transport import CookieTransport, HeaderTransport

from fastid.api.exceptions import ClientError
from fastid.auth.config import auth_settings
from fastid.auth.models import User
from fastid.auth.use_cases import AuthUseCases
from fastid.auth.utils import AuthBus

auth_flows: Iterable[Callable[..., Any]] = [
    APIKeyHeader(name="Authorization", scheme_name="BearerToken", auto_error=False),
    APIKeyCookie(name="fastidaccesstoken", scheme_name="BearerCookie", auto_error=False),
    OAuth2PasswordBearer(tokenUrl="/api/v1/token", scheme_name="Password", auto_error=False),
]

AuthDep = Annotated[AuthUseCases, Depends()]

header_transport = HeaderTransport()
cookie_transport = CookieTransport(name="fastidaccesstoken", max_age=auth_settings.jwt_access_expires_in)
auth_bus = AuthBus(header_transport, cookie_transport)


async def get_user(
    service: AuthDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    return await service.get_userinfo(token)


user_dep = Depends(get_user)
UserDep = Annotated[User, user_dep]

vt_transport = CookieTransport(
    name="fastidverifytoken",
    scheme_name="VerifyTokenCookie",
    max_age=auth_settings.jwt_verify_token_expires_in,
)


async def get_user_by_vt(
    service: AuthDep,
    token: Annotated[str, Depends(vt_transport)],
) -> User:
    return await service.get_userinfo(token, token_type="verify")  # noqa: S106


UserVTDep = Annotated[User, Depends(get_user_by_vt)]


async def get_user_or_none(service: AuthDep, request: Request) -> User | None:
    token = auth_bus.parse_request(request, auto_error=False)
    if token is None:
        return None
    try:
        return await service.get_userinfo(token)
    except ClientError:
        return None


UserOrNoneDep = Annotated[User | None, Depends(get_user_or_none)]
