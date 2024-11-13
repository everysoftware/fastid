import datetime
from typing import Annotated

from fastapi import Depends

from app.api.config import api_settings
from app.auth.dependencies import AuthDep
from app.auth.models import User
from app.authlib.backend import OAuth2Backend
from app.authlib.config import auth_settings
from app.authlib.schemas import TokenConfig
from app.authlib.tokens import TokenManager
from app.authlib.transports import HeaderTransport, CookieTransport, AuthBus
from app.base.types import UUID

access_config = TokenConfig(
    type="access",
    issuer=api_settings.discovery_name,
    algorithm=auth_settings.jwt_algorithm,
    private_key=auth_settings.jwt_private_key.read_text(),
    public_key=auth_settings.jwt_public_key.read_text(),
    expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expire),
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
