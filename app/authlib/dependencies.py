import datetime
from typing import Annotated

from fastapi import Depends

from app.authlib.backend import OAuth2Backend
from app.authlib.schemas import TokenConfig
from app.authlib.tokens import TokenManager
from app.authlib.transports import HeaderTransport, CookieTransport, AuthBus
from app.runner.config import settings
from app.domain.types import UUID
from app.auth.dependencies import AuthDep
from app.auth.schemas import User

access_config = TokenConfig(
    type="access",
    issuer=settings.auth.jwt_issuer,
    algorithm=settings.auth.jwt_algorithm,
    private_key=settings.auth.jwt_private_key.read_text(),
    public_key=settings.auth.jwt_public_key.read_text(),
    expires_in=datetime.timedelta(seconds=settings.auth.jwt_access_expire),
)

token_manager = TokenManager(access_config)
auth_backend = OAuth2Backend(token_manager)

header_transport = HeaderTransport()
cookie_transport = CookieTransport()
auth_bus = AuthBus(header_transport, cookie_transport)


async def get_user(
    service: AuthDep,
    token: Annotated[str, Depends(auth_bus)],
) -> User:
    payload = auth_backend.validate_access(token)
    return await service.get_one(UUID(payload.sub))


UserDep = Annotated[User, Depends(get_user)]
