import secrets

from passlib.context import CryptContext

crypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp() -> str:
    return str(secrets.choice(range(100_000, 1_000_000)))
