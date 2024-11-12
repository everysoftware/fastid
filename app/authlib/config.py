from pathlib import Path

from app.domain.schemas import BaseSettings


class AuthSettings(BaseSettings):
    jwt_issuer: str = "fastid"
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_expire: int = 60 * 60  # 1 hour
    jwt_refresh_expire: int = 30 * 24 * 60  # 30 days

    first_user_email: str = "user@example.com"
    first_user_password: str = "password"
    admin_email: str = "admin@example.com"
    admin_password: str = "changethis"
    code_length: int = 6
    code_expires_in: int = 5 * 60
