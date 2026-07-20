import base64
import hashlib
import hmac
import json
import time
from typing import Any
from uuid import uuid4

SECRET = f"whsec_{base64.b64encode(b'test-webhook-secret').decode()}"


def payload(event_id: str | None = None) -> dict[str, Any]:
    event_id = event_id or str(uuid4())
    return {
        "event": {"event_id": event_id, "event_type": "user_registration", "timestamp": int(time.time())},
        "data": {"user": {"id": str(uuid4()), "email": "person@example.com"}},
    }


def headers_for(
    body: bytes,
    event_id: str,
    *,
    secret: str = SECRET,
    timestamp: int | None = None,
) -> dict[str, str]:
    timestamp = timestamp or int(time.time())
    key = base64.b64decode(secret.removeprefix("whsec_"), validate=True)
    signed = b".".join((event_id.encode(), str(timestamp).encode(), body))
    signature = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    return {
        "webhook-id": event_id,
        "webhook-timestamp": str(timestamp),
        "webhook-signature": f"v1,{signature}",
        "content-type": "application/json",
    }


def signed_request(value: dict[str, Any], secret: str = SECRET) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()
    event_id = str(value["event"]["event_id"])
    return body, headers_for(body, event_id, secret=secret)
