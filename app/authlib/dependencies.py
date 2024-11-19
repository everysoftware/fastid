import datetime

from app.auth.config import auth_settings
from app.authlib.backend import BackendConfig, TokenBackend
from app.authlib.openid import JWTParams
from app.authlib.transports import HeaderTransport, CookieTransport, AuthBus
from app.main.config import main_settings

conf = BackendConfig()
conf.add_type(
    "access",
    JWTParams(
        issuer=main_settings.base_url,
        algorithm=auth_settings.jwt_algorithm,
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expire),
    ),
)
conf.add_type(
    "id",
    JWTParams(
        issuer=main_settings.base_url,
        algorithm=auth_settings.jwt_algorithm,
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
    ),
)
conf.add_type(
    "refresh",
    JWTParams(
        issuer=main_settings.base_url,
        algorithm=auth_settings.jwt_algorithm,
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(
            seconds=auth_settings.jwt_refresh_expire
        ),
    ),
)
token_backend = TokenBackend(conf)

header_transport = HeaderTransport()
cookie_transport = CookieTransport()
auth_bus = AuthBus(header_transport, cookie_transport)
