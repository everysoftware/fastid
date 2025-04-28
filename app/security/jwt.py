import datetime

from auth365.jwt import JWTBackend
from auth365.schemas import JWTConfig

from app.auth.config import auth_settings
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

jwt_backend = JWTBackend(*conf)
