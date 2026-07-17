import base64
import hashlib
import hmac
import json
import time
from collections.abc import Mapping
from typing import Any

from fastid.database.utils import UUIDv7, uuid
from fastid.webhooks.config import webhook_settings
from fastid.webhooks.models import generate_webhook_secret
from fastid.webhooks.schemas import SignatureAlgorithm

HASH_FUNCTIONS = {
    SignatureAlgorithm.sha256: hashlib.sha256,
    SignatureAlgorithm.sha512: hashlib.sha512,
    SignatureAlgorithm.sha1: hashlib.sha1,
}

STANDARD_ID_HEADER = "webhook-id"
STANDARD_TIMESTAMP_HEADER = "webhook-timestamp"
STANDARD_SIGNATURE_HEADER = "webhook-signature"


def serialize_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def generate_secret() -> str:
    return generate_webhook_secret()


def _secret_bytes(secret_key: str) -> bytes:
    if not secret_key.startswith("whsec_"):
        return secret_key.encode()
    try:
        return base64.b64decode(secret_key.removeprefix("whsec_"), validate=True)
    except ValueError as exc:
        msg = "Invalid whsec_ webhook secret"
        raise ValueError(msg) from exc


def generate_standard_signature(body: bytes, webhook_id: str, timestamp: int, secret_key: str) -> str:
    signed = b".".join((webhook_id.encode(), str(timestamp).encode(), body))
    digest = hmac.new(_secret_bytes(secret_key), signed, hashlib.sha256).digest()
    return f"v1,{base64.b64encode(digest).decode()}"


def generate_delivery_headers(  # noqa: PLR0913
    payload: dict[str, Any], body: bytes, event_id: str, delivery_id: str, timestamp: int, secret_key: str
) -> dict[str, str]:
    return generate_headers(payload, timestamp, delivery_id, secret_key) | {
        STANDARD_ID_HEADER: event_id,
        STANDARD_TIMESTAMP_HEADER: str(timestamp),
        STANDARD_SIGNATURE_HEADER: generate_standard_signature(body, event_id, timestamp, secret_key),
        "Content-Type": "application/json",
        "User-Agent": webhook_settings.user_agent,
    }


def generate_headers(
    payload: dict[str, Any],
    timestamp: int,
    webhook_id: str,
    secret_key: str,
    *,
    algorithm: SignatureAlgorithm = webhook_settings.signature_algorithm,
) -> dict[str, str]:
    signature = generate_signature(payload, webhook_id, timestamp, secret_key, algorithm=algorithm)
    return {
        webhook_settings.id_header: webhook_id,
        webhook_settings.timestamp_header: str(timestamp),
        webhook_settings.signature_header: signature,
    }


def generate_signature(
    payload: dict[str, Any],
    webhook_id: str,
    timestamp: int,
    secret_key: str,
    *,
    algorithm: SignatureAlgorithm = webhook_settings.signature_algorithm,
) -> str:
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_str = f"{webhook_id}.{timestamp}.{payload_str}"
    hash_func = HASH_FUNCTIONS[algorithm]
    hmac_obj = hmac.new(key=secret_key.encode(), msg=payload_str.encode(), digestmod=hash_func)
    return hmac_obj.hexdigest()


def verify_headers(
    payload: dict[str, Any],
    headers: dict[str, str],
    secret_key: str,
    tolerance_seconds: int = webhook_settings.tolerance_seconds,
) -> bool:
    try:
        timestamp = int(headers[webhook_settings.timestamp_header])
        webhook_id = headers[webhook_settings.id_header]
        received_signature = headers[webhook_settings.signature_header]
    except (KeyError, ValueError):  # pragma: nocover
        return False

    if not all([timestamp, webhook_id, received_signature]):
        return False

    if not is_timestamp_valid(timestamp, tolerance_seconds):
        return False

    expected_signature = generate_signature(payload, webhook_id, timestamp, secret_key)
    return hmac.compare_digest(received_signature, expected_signature)


def verify_standard_headers(
    body: bytes,
    headers: Mapping[str, str],
    secret_key: str,
    tolerance_seconds: int = webhook_settings.tolerance_seconds,
) -> bool:
    normalized = {key.lower(): value for key, value in headers.items()}
    try:
        timestamp = int(normalized[STANDARD_TIMESTAMP_HEADER])
        webhook_id = normalized[STANDARD_ID_HEADER]
        signatures = normalized[STANDARD_SIGNATURE_HEADER].split()
    except (KeyError, ValueError):
        return False
    if not webhook_id or not signatures or not is_timestamp_valid(timestamp, tolerance_seconds):
        return False
    expected = generate_standard_signature(body, webhook_id, timestamp, secret_key)
    return any(hmac.compare_digest(signature, expected) for signature in signatures)


def get_event_id() -> UUIDv7:
    return uuid()


def get_webhook_id() -> UUIDv7:
    return uuid()


def get_timestamp() -> int:
    return int(time.time())


def is_timestamp_valid(timestamp: int, tolerance_seconds: int) -> bool:
    current_time = int(time.time())
    return abs(current_time - timestamp) <= tolerance_seconds
