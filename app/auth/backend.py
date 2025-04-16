import datetime

from auth365.fastapi.transport import CookieTransport, HeaderTransport
from auth365.jwt import JWTBackend
from auth365.schemas import JWTConfig
from passlib.context import CryptContext

from app.auth.config import auth_settings
from app.auth.utils import AuthBus
from app.main.config import main_settings

conf = [
    JWTConfig(
        type="access",
        issuer=main_settings.base_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expires_in),
    ),
    JWTConfig(
        type="refresh",
        issuer=main_settings.base_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_refresh_expires_in),
    ),
    JWTConfig(
        type="verify",
        issuer=main_settings.base_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_verify_token_expires_in),
    ),
    JWTConfig(
        type="id",
        issuer=main_settings.base_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
    ),
]

token_backend = JWTBackend(*conf)
header_transport = HeaderTransport()
cookie_transport = CookieTransport(name="fastidaccesstoken", max_age=auth_settings.jwt_access_expires_in)
auth_bus = AuthBus(header_transport, cookie_transport)

verify_token_transport = CookieTransport(
    name="fastidverifytoken",
    scheme_name="VerifyTokenCookie",
    max_age=auth_settings.jwt_verify_token_expires_in,
)

crypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
