import datetime

from app.main.config import api_settings
from app.auth.config import auth_settings
from app.authlib.backend import BackendConfig, TokenBackend
from app.authlib.schemas import TypeParams
from app.authlib.transports import HeaderTransport, CookieTransport, AuthBus

conf = BackendConfig()
conf.add_type(
    "access",
    TypeParams(
        issuer=api_settings.discovery_name,
        algorithm=auth_settings.jwt_algorithm,
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expire),
    ),
)
token_backend = TokenBackend(conf)

header_transport = HeaderTransport()
cookie_transport = CookieTransport()
auth_bus = AuthBus(header_transport, cookie_transport)
