import hashlib
import hmac
import json
import time
from typing import Any

from fastid.database.utils import UUIDv7, uuid
from fastid.webhooks.config import webhook_settings
from fastid.webhooks.schemas import SignatureAlgorithm

HASH_FUNCTIONS = {
    SignatureAlgorithm.sha256: hashlib.sha256,
    SignatureAlgorithm.sha512: hashlib.sha512,
    SignatureAlgorithm.sha1: hashlib.sha1,
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


def get_event_id() -> UUIDv7:
    return uuid()


def get_webhook_id() -> UUIDv7:
    return uuid()


def get_timestamp() -> int:
    return int(time.time())


def is_timestamp_valid(timestamp: int, tolerance_seconds: int) -> bool:
    current_time = int(time.time())
    return abs(current_time - timestamp) <= tolerance_seconds
