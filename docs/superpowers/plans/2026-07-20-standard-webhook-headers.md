# Standard Webhook Headers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove FastID's legacy `X-Webhook-*` authentication protocol so every delivery uses only Standard Webhooks headers.

**Architecture:** Keep one signing path in `fastid.security.webhooks`: serialize the payload once, sign the exact bytes with the stable Webhook ID, and send only the three standard authentication headers. Remove the legacy configurable protocol from settings and schemas, then update the worker and tutorial to the smaller contract.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, pytest, Ruff, mypy

## Global Constraints

- Preserve `webhook-id` as the stable Webhook ID and consumer idempotency key.
- Sign the exact bytes `webhook-id.webhook-timestamp.raw_body` with HMAC-SHA256.
- Keep the `v1,<base64>` signature representation and `whsec_<base64>` secrets.
- Do not change payload fields, retry behavior, persisted deliveries, or endpoint secret generation.
- Do not modify the user's existing `docker/Dockerfile` changes.
- Prefix every shell command with `rtk`.

## File structure

- `fastid/security/webhooks.py`: the sole standard signing and verification implementation.
- `fastid/webhooks/config.py`: delivery policy settings; no consumer-controlled authentication protocol settings.
- `fastid/webhooks/schemas.py`: webhook payload schemas; no obsolete signing algorithm enum.
- `fastid/webhooks/worker.py`: signs a claimed delivery with its stable Webhook ID and exact body.
- `tests/security/test_webhooks.py`: standard header generation and verification behavior.
- `tests/mocks.py`: shared webhook payload, timestamp, and event ID fixtures only.
- `tests/api/webhooks/test_worker_delivery.py`: existing end-to-end worker/header contract test.
- `docs/docs/tutorial/webhooks.md`: documents the single supported header family.

---

### Task 1: Make Standard Webhooks the only generated and verified protocol

**Files:**
- Modify: `tests/security/test_webhooks.py`
- Modify: `tests/mocks.py:8-10,141-153`
- Modify: `fastid/security/webhooks.py`

**Interfaces:**
- Produces: `generate_delivery_headers(body: bytes, webhook_id: str, timestamp: int, secret_key: str) -> dict[str, str]`
- Preserves: `verify_standard_headers(body: bytes, headers: Mapping[str, str], secret_key: str, tolerance_seconds: int = 300) -> bool`
- Preserves: `serialize_payload(payload: dict[str, Any]) -> bytes`

- [ ] **Step 1: Replace legacy-oriented security tests with the single-protocol contract**

Replace `tests/security/test_webhooks.py` with:

```python
import pytest

import fastid.security.webhooks as webhook_security
from fastid.security.webhooks import (
    generate_delivery_headers,
    generate_secret,
    serialize_payload,
    verify_standard_headers,
)
from tests.mocks import WEBHOOK_ID, WEBHOOK_PAYLOAD, WEBHOOK_TIMESTAMP


@pytest.mark.parametrize("secret", ["plain-secret", generate_secret()])
def test_verify_standard_headers(secret: str) -> None:
    body = serialize_payload(WEBHOOK_PAYLOAD)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, secret)

    assert set(headers) == {
        "webhook-id",
        "webhook-timestamp",
        "webhook-signature",
        "Content-Type",
        "User-Agent",
    }
    assert verify_standard_headers(body, headers, secret)
    assert not verify_standard_headers(body + b" ", headers, secret)
    assert not verify_standard_headers(body, headers, "wrong-secret")


def test_standard_signature_uses_exact_utf8_body() -> None:
    payload = {"message": "Привет"}
    body = serialize_payload(payload)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, "secret")

    assert b"\\u" not in body
    assert verify_standard_headers(body, {key.upper(): value for key, value in headers.items()}, "secret")


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"webhook-id": WEBHOOK_ID, "webhook-timestamp": "invalid", "webhook-signature": "v1,value"},
        {"webhook-id": "", "webhook-timestamp": str(WEBHOOK_TIMESTAMP), "webhook-signature": "v1,value"},
        {"webhook-id": WEBHOOK_ID, "webhook-timestamp": str(WEBHOOK_TIMESTAMP), "webhook-signature": ""},
    ],
)
def test_verify_standard_headers_rejects_malformed_headers(headers: dict[str, str]) -> None:
    assert not verify_standard_headers(b"{}", headers, "secret")


def test_verify_standard_headers_rejects_stale_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    body = serialize_payload(WEBHOOK_PAYLOAD)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, "secret")
    monkeypatch.setattr(webhook_security.time, "time", lambda: WEBHOOK_TIMESTAMP + 301)

    assert not verify_standard_headers(body, headers, "secret")


def test_invalid_prefixed_secret_is_a_configuration_error() -> None:
    with pytest.raises(ValueError, match="Invalid whsec_ webhook secret"):
        generate_delivery_headers(b"{}", WEBHOOK_ID, WEBHOOK_TIMESTAMP, "whsec_not-base64")
```

In `tests/mocks.py`, remove the `webhook_settings` import and remove `WEBHOOK_SECRET_KEY`,
`WEBHOOK_EXPIRED_TIMESTAMP`, `WEBHOOK_WRONG_SECRET_KEY`, and `WEBHOOK_TEST_DATA`. Retain exactly these shared values:

```python
WEBHOOK_PAYLOAD = {"test": {"test1": 1, "test2": "hello", "hello3": True}}
WEBHOOK_TIMESTAMP = get_timestamp()
WEBHOOK_ID = str(get_webhook_id())
```

- [ ] **Step 2: Run the rewritten tests and verify the old API fails**

Run:

```powershell
rtk pytest tests/security/test_webhooks.py -q
```

Expected: FAIL because the existing `generate_delivery_headers()` still requires `payload` and `delivery_id`, and generated deliveries still contain legacy headers.

- [ ] **Step 3: Replace the security module with the standard-only implementation**

Replace `fastid/security/webhooks.py` with:

```python
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


def generate_delivery_headers(body: bytes, webhook_id: str, timestamp: int, secret_key: str) -> dict[str, str]:
    return {
        STANDARD_ID_HEADER: webhook_id,
        STANDARD_TIMESTAMP_HEADER: str(timestamp),
        STANDARD_SIGNATURE_HEADER: generate_standard_signature(body, webhook_id, timestamp, secret_key),
        "Content-Type": "application/json",
        "User-Agent": webhook_settings.user_agent,
    }


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
```

- [ ] **Step 4: Run focused security checks**

Run:

```powershell
rtk pytest tests/security/test_webhooks.py -q
rtk ruff check fastid/security/webhooks.py tests/security/test_webhooks.py tests/mocks.py
rtk mypy fastid/security/webhooks.py tests/security/test_webhooks.py
```

Expected: all tests pass and both static checks exit successfully.

- [ ] **Step 5: Commit the standard-only security contract**

```powershell
rtk git add fastid/security/webhooks.py tests/security/test_webhooks.py tests/mocks.py
rtk git commit -m "refactor: use standard webhook signatures only"
```

Expected: commit succeeds without staging `docker/Dockerfile`.

---

### Task 2: Remove the obsolete configuration and schema surface

**Files:**
- Modify: `fastid/webhooks/config.py:1-12`
- Modify: `fastid/webhooks/schemas.py:1-16`

**Interfaces:**
- Consumes: `webhook_settings.tolerance_seconds` and `webhook_settings.user_agent` used by Task 1.
- Produces: `WebhookSettings` containing delivery policy only; payload schema classes remain unchanged.

- [ ] **Step 1: Prove the obsolete API is still present**

Run:

```powershell
rtk rg -n "SignatureAlgorithm|signature_algorithm|signature_header|timestamp_header|id_header" fastid
```

Expected: matches in `fastid/webhooks/config.py` and `fastid/webhooks/schemas.py`; no matches should remain after this task.

- [ ] **Step 2: Remove legacy settings while preserving delivery policy**

Make the beginning of `fastid/webhooks/config.py` exactly:

```python
from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class WebhookSettings(BaseSettings):
    tolerance_seconds: int = 300
    page_expires_in_seconds: int = 60
```

Leave every setting from `retry_delays_seconds` through `user_agent`, the `model_config`, and the `webhook_settings`
instance unchanged.

- [ ] **Step 3: Remove the unused signing enum**

Make the imports and first model in `fastid/webhooks/schemas.py` exactly:

```python
from typing import Any
from uuid import UUID

from pydantic import Field

from fastid.auth.schemas import UserDTO
from fastid.core.schemas import BaseModel
from fastid.webhooks.models import WebhookType


class SendWebhookRequest(BaseModel):
    type: WebhookType
    payload: dict[str, Any] = Field(default_factory=dict)
```

Leave `Event`, `WebhookPayload`, `Webhook`, `WebhookData`, `UserWebhookData`, and `UserWebhook` unchanged.

- [ ] **Step 4: Verify removal and static correctness**

Run:

```powershell
rtk rg -n "SignatureAlgorithm|signature_algorithm|signature_header|timestamp_header|id_header" fastid
rtk ruff check fastid/webhooks/config.py fastid/webhooks/schemas.py
rtk mypy fastid/webhooks/config.py fastid/webhooks/schemas.py
```

Expected: `rg` prints no matches; Ruff and mypy exit successfully.

- [ ] **Step 5: Commit the public-surface cleanup**

```powershell
rtk git add fastid/webhooks/config.py fastid/webhooks/schemas.py
rtk git commit -m "refactor: remove legacy webhook configuration"
```

Expected: commit succeeds without staging `docker/Dockerfile`.

---

### Task 3: Update the worker and documentation to the single protocol

**Files:**
- Modify: `fastid/webhooks/worker.py:131-143`
- Test: `tests/api/webhooks/test_worker_delivery.py:39-73`
- Modify: `docs/docs/tutorial/webhooks.md:7-18`

**Interfaces:**
- Consumes: `generate_delivery_headers(body: bytes, webhook_id: str, timestamp: int, secret_key: str)` from Task 1.
- Preserves: worker delivery requests contain a valid signature for the exact body and endpoint secret.

- [ ] **Step 1: Run the existing worker contract test against the narrowed function**

Run:

```powershell
rtk pytest tests/api/webhooks/test_worker_delivery.py::test_worker_records_delivery_outcome -q
```

Expected: FAIL with a `TypeError` because the worker still passes the payload and internal delivery ID.

- [ ] **Step 2: Update the worker to sign only the stable Webhook ID and raw body**

Replace the header-generation block in `WebhookWorker._process()` with:

```python
        headers = generate_delivery_headers(
            body,
            str(delivery.id),
            timestamp,
            delivery.endpoint_secret,
        )
```

Do not change payload serialization, sending, or attempt recording.

- [ ] **Step 3: Run the worker webhook tests**

Run:

```powershell
rtk pytest tests/api/webhooks/test_worker_delivery.py tests/webhooks/test_worker.py tests/webhooks/test_sender.py -q
```

Expected: all tests pass, including signature verification at `test_worker_delivery.py:70-71`.

- [ ] **Step 4: Remove the compatibility claim from the tutorial**

Replace the opening of the request-format section in `docs/docs/tutorial/webhooks.md` with:

```markdown
## Request format

Each request is a JSON `POST` with Standard Webhooks headers:

- `webhook-id`: Webhook ID, unchanged for retries of the same delivery.
- `webhook-timestamp`: Unix timestamp for the delivery attempt.
- `webhook-signature`: `v1,<base64 HMAC-SHA256>` signature.
```

Keep the raw-body verification explanation and all later delivery/security documentation unchanged.

- [ ] **Step 5: Verify there are no legacy protocol references**

Run:

```powershell
rtk rg -n -i "x-webhook|generate_headers|generate_signature|verify_headers|SignatureAlgorithm" fastid tests docs/docs
rtk ruff check fastid tests
rtk mypy fastid
rtk pytest tests/security/test_webhooks.py tests/api/webhooks tests/webhooks -q
rtk git diff --check
```

Expected: `rg` prints no matches; Ruff, mypy, pytest, and `git diff --check` all exit successfully.

- [ ] **Step 6: Commit the worker and tutorial migration**

```powershell
rtk git add fastid/webhooks/worker.py docs/docs/tutorial/webhooks.md
rtk git commit -m "refactor: send only standard webhook headers"
```

Expected: commit succeeds without staging `docker/Dockerfile`.

---

### Task 4: Run final regression verification

**Files:**
- Verify only; do not modify unrelated files.

**Interfaces:**
- Consumes: the standard-only webhook contract completed in Tasks 1-3.
- Produces: evidence that the cleanup is ready for the webhook examples.

- [ ] **Step 1: Run the complete project checks**

```powershell
rtk pytest -q
rtk ruff check .
rtk mypy fastid
rtk git diff --check
```

Expected: all commands exit successfully. If an unrelated pre-existing failure occurs, record its exact command and
output without modifying unrelated code.

- [ ] **Step 2: Confirm scope and history**

```powershell
rtk git status --short
rtk git log -4 --oneline
```

Expected: only the user's pre-existing `docker/Dockerfile` changes remain; the three cleanup commits follow the design
documentation commit `2f31b19`.
