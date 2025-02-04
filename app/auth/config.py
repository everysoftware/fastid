from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings
from app.main.config import main_settings


class AuthSettings(BaseSettings):
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_access_expires_in: int = 60 * 60  # 1 hour
    jwt_refresh_expires_in: int = 30 * 24 * 60  # 30 days
    jwt_verify_token_expires_in: int = 5 * 60  # 5 minutes

    authorization_code_expires_in: int = 5 * 60  # 5 minutes
    verification_code_expires_in: int = 5 * 60  # 5 minutes

    @property
    def issuer(self) -> str:
        return main_settings.base_url

    @property
    def authorization_endpoint(self) -> str:
        return f"{main_settings.base_url}/authorize"

    @property
    def registration_endpoint(self) -> str:
        return f"{main_settings.base_url}/register"

    @property
    def token_endpoint(self) -> str:
        return f"{main_settings.api_url}/token"

    @property
    def userinfo_endpoint(self) -> str:
        return f"{main_settings.api_url}/userinfo"

    @property
    def jwks_uri(self) -> str:
        return f"{main_settings.base_url}/.well-known/jwks.json"

    model_config = SettingsConfigDict(env_prefix="auth_")


auth_settings = AuthSettings()
