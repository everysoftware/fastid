from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings
from app.main.config import main_settings


class AuthSettings(BaseSettings):
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_expire: int = 60 * 60  # 1 hour
    jwt_refresh_expire: int = 30 * 24 * 60  # 30 days

    default_user_email: str = "user@example.com"
    default_user_password: str = "password"
    admin_email: str = "admin@example.com"
    admin_password: str = "changethis"

    authorization_code_expires_in: int = 5 * 60
    verification_code_expires_in: int = 5 * 60

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
