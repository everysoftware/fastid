from collections.abc import Sequence
from pathlib import Path

from fastid.core.schemas import BaseSettings


class AuthSettings(BaseSettings):
    server_url: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_id_algorithm: str = "RS256"
    jwt_key: Path = Path("certs") / "secret.key"
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_access_expires_in: int = 60 * 60  # 1 hour
    jwt_refresh_expires_in: int = 30 * 24 * 60  # 30 days
    jwt_verify_token_expires_in: int = 5 * 60  # 5 minutes

    authorization_code_expires_in: int = 5 * 60  # 5 minutes
    verification_code_expires_in: int = 5 * 60  # 5 minutes

    hash_schemas: Sequence[str] = ["argon2", "bcrypt"]  # Supports reverse compatibility
    hash_default: str = "argon2"
    argon2_time_cost: int = 2
    argon2_memory_cost: int = 19456
    argon2_parallelism: int = 1
    argon2_salt_len: int = 16
    argon2_hash_len: int = 32

    app_expires_in_seconds: int = 60


auth_settings = AuthSettings()
