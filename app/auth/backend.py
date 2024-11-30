import datetime

from passlib.context import CryptContext

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
        expires_in=datetime.timedelta(
            seconds=auth_settings.jwt_access_expires_in
        ),
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
            seconds=auth_settings.jwt_refresh_expires_in
        ),
    ),
)
conf.add_type(
    "verify",
    JWTParams(
        issuer=main_settings.base_url,
        algorithm=auth_settings.jwt_algorithm,
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(
            seconds=auth_settings.jwt_verify_token_expires_in
        ),
    ),
)
token_backend = TokenBackend(conf)

header_transport = HeaderTransport()
cookie_transport = CookieTransport(max_age=auth_settings.jwt_access_expires_in)
auth_bus = AuthBus(header_transport, cookie_transport)

verify_token_transport = CookieTransport(
    name="fastidverifytoken",
    scheme_name="VerifyTokenCookie",
    max_age=auth_settings.jwt_verify_token_expires_in,
)

hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
