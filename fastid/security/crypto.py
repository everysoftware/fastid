import secrets

from passlib.context import CryptContext

crypt_ctx = CryptContext(
    schemes=["argon2", "bcrypt"],  # Supports reverse compatibility
    default="argon2",
    argon2__time_cost=3,
    argon2__memory_cost=65536,
    argon2__parallelism=4,
    argon2__salt_len=16,
    argon2__hash_len=32,
)


def generate_otp() -> str:
    return str(secrets.choice(range(100_000, 1_000_000)))
