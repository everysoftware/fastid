import base64
import datetime
import hashlib
import hmac
import os
from typing import Any

from fastid.integrations.exceptions import ExpirationError, HashMismatchError


def generate_random_state(length: int = 64) -> str:
    bytes_length = int(length * 3 / 4)
    return base64.urlsafe_b64encode(os.urandom(bytes_length)).decode("utf-8")


def generate_pkce_verifier(state: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), state.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def generate_pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def replace_localhost(url: Any) -> str:
    return str(url).replace("localhost", "127.0.0.1", 1)


def compute_hmac_sha256(payload: dict[str, Any], secret_key: str) -> str:
    data_check_string = "\n".join(sorted(f"{k}={v}" for k, v in payload.items()))
    return hmac.new(
        hashlib.sha256(secret_key.encode()).digest(),
        data_check_string.encode(),
        "sha256",
    ).hexdigest()


def verify_hmac_sha256(payload: dict[str, Any], expected_hash: str, secret_key: str) -> None:
    computed_hash = compute_hmac_sha256(payload, secret_key)
    if not hmac.compare_digest(computed_hash, expected_hash):
        raise HashMismatchError


def check_expiration(payload: dict[str, Any], expires_in: int = 300) -> None:
    dt = datetime.datetime.fromtimestamp(payload["auth_date"], tz=datetime.UTC)
    now = datetime.datetime.now(tz=datetime.UTC)
    if now - dt > datetime.timedelta(seconds=expires_in):
        raise ExpirationError
