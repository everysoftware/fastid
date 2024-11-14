from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


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
    code_length: int = 6
    code_expires_in: int = 5 * 60

    model_config = SettingsConfigDict(env_prefix="auth_")


auth_settings = AuthSettings()