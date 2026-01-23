import secrets

from passlib.context import CryptContext

from fastid.auth.config import auth_settings

crypt_ctx = CryptContext(
    schemes=auth_settings.hash_schemas,
    default=auth_settings.hash_default,
    argon2__time_cost=auth_settings.argon2_time_cost,
    argon2__memory_cost=auth_settings.argon2_memory_cost,
    argon2__parallelism=auth_settings.argon2_parallelism,
    argon2__salt_len=auth_settings.argon2_salt_len,
    argon2__hash_len=auth_settings.argon2_hash_len,
)


def generate_otp() -> str:
    return str(secrets.choice(range(100_000, 1_000_000)))
