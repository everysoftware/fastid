import datetime

from fastid.auth.config import auth_settings
from fastid.core.config import core_settings
from fastid.security.manager import JWTManager
from fastid.security.schemas import JWTConfig

kwargs = {
    "algorithm": auth_settings.jwt_algorithm,
    "issuer": core_settings.frontend_url,
    "key": auth_settings.jwt_key.read_text(),
}
id_kwargs = {
    "algorithm": auth_settings.jwt_id_algorithm,
    "issuer": core_settings.frontend_url,
    "private_key": auth_settings.jwt_private_key.read_text(),
    "public_key": auth_settings.jwt_public_key.read_text(),
}

conf = [
    JWTConfig(type="access", expires_in=datetime.timedelta(seconds=auth_settings.jwt_access_expires_in), **kwargs),
    JWTConfig(type="refresh", expires_in=datetime.timedelta(seconds=auth_settings.jwt_refresh_expires_in), **kwargs),
    JWTConfig(
        type="verify", expires_in=datetime.timedelta(seconds=auth_settings.jwt_verify_token_expires_in), **kwargs
    ),
    JWTConfig(type="id", **id_kwargs),
]

jwt_backend = JWTManager(*conf)
