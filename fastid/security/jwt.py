import datetime

from fastid.auth.config import auth_settings
from fastid.core.config import core_settings
from fastid.security.manager import JWTManager
from fastid.security.schemas import JWTConfig

conf = [
    JWTConfig(
        type="access",
        issuer=core_settings.frontend_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expires_in),
    ),
    JWTConfig(
        type="refresh",
        issuer=core_settings.frontend_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_refresh_expires_in),
    ),
    JWTConfig(
        type="verify",
        issuer=core_settings.frontend_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
        expires_in=datetime.timedelta(seconds=auth_settings.jwt_verify_token_expires_in),
    ),
    JWTConfig(
        type="id",
        issuer=core_settings.frontend_url,
        algorithm="RS256",
        private_key=auth_settings.jwt_private_key.read_text(),
        public_key=auth_settings.jwt_public_key.read_text(),
    ),
]

jwt_backend = JWTManager(*conf)
