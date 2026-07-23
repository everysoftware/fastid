# Webhook Quickstart Timestamp Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject malformed and replay-prone timestamps in the `webhook_quickstart` example.

**Architecture:** Keep timestamp verification inline in the quickstart's request handler so the security flow remains linear and copyable. Parse the signed timestamp header as a Unix timestamp, enforce the same five-minute past/future tolerance as the advanced example, and only then verify the signature.

**Tech Stack:** Python 3.12, FastAPI, pytest, Starlette `TestClient`

## Global Constraints

- The allowed timestamp difference is exactly 300 seconds in either direction.
- Malformed timestamp headers return HTTP 400 with `Invalid webhook-timestamp header`.
- Out-of-tolerance timestamp headers return HTTP 400 with `Webhook timestamp is outside the allowed tolerance`.
- Invalid signatures continue to return HTTP 401.
- The unmodified timestamp header string remains part of the signature input.
- Only the quickstart example and its tests are changed.

---

## File Structure

- `examples/webhook_quickstart.py`: Continue to own the complete, standalone quickstart receiver, including inline timestamp and signature verification.
- `tests/examples/test_webhook_quickstart.py`: Cover accepted current timestamps and rejected malformed, stale, and excessively future timestamps through HTTP requests.
- `tests/examples/webhook_helpers.py`: Reuse without modification to generate signatures over chosen timestamp header values.

### Task 1: Verify Quickstart Webhook Timestamp Freshness

**Files:**

- Modify: `tests/examples/test_webhook_quickstart.py:1-65`
- Modify: `examples/webhook_quickstart.py:1-96`

**Interfaces:**

- Consumes: `headers_for(body: bytes, webhook_id: str, *, secret: str = SECRET, timestamp: int | str | None = None) -> dict[str, str]`
- Produces: HTTP 400 responses for malformed or out-of-tolerance `webhook-timestamp` headers; no new public Python interface.

- [ ] **Step 1: Write failing timestamp rejection tests**

Add `import time` to `tests/examples/test_webhook_quickstart.py`. Replace
`test_treats_webhook_id_and_timestamp_as_opaque_signature_inputs` with these
tests:

```python
def test_rejects_malformed_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    value = payload()
    body, _ = signed_request(value)
    headers = headers_for(body, "opaque-webhook-id", timestamp="opaque-timestamp")

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid webhook-timestamp header"}


@pytest.mark.parametrize("offset", [-3600, 3600])
def test_rejects_timestamp_outside_tolerance(
    monkeypatch: pytest.MonkeyPatch,
    offset: int,
) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    value = payload()
    body, _ = signed_request(value)
    headers = headers_for(body, "event-1", timestamp=int(time.time()) + offset)

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Webhook timestamp is outside the allowed tolerance"}
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
rtk pytest -q tests/examples/test_webhook_quickstart.py
```

Expected: three timestamp cases fail because the current quickstart accepts
opaque, stale, and future timestamp strings and returns HTTP 204 instead of
HTTP 400. Existing tests pass.

- [ ] **Step 3: Implement minimal inline timestamp verification**

In `examples/webhook_quickstart.py`, add the standard-library import and
tolerance constant:

```python
import os
import time
from collections.abc import AsyncIterator

# ...

log = logging.getLogger(__name__)

TIMESTAMP_TOLERANCE_SECONDS = 300
```

Replace the timestamp-header portion of `receive_webhook` with:

```python
    webhook_id = _required_header(request, "webhook-id")
    timestamp_value = _required_header(request, "webhook-timestamp")
    signatures = _required_header(request, "webhook-signature")
    try:
        timestamp = int(timestamp_value)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook-timestamp header") from exc
    if abs(int(time.time()) - timestamp) > TIMESTAMP_TOLERANCE_SECONDS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Webhook timestamp is outside the allowed tolerance")
    if not verify_signature(body, webhook_id, timestamp_value, signatures, request.app.state.webhook_secret):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid webhook signature")
```

Keep `verify_signature` accepting `timestamp: str` so it signs the exact header
value instead of its parsed integer representation.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
rtk pytest -q tests/examples/test_webhook_quickstart.py
```

Expected: all quickstart tests pass with no warnings or errors.

- [ ] **Step 5: Run relevant example regression tests**

Run:

```powershell
rtk pytest -q tests/examples
```

Expected: all example tests pass with no warnings or errors.

- [ ] **Step 6: Run lint checks for changed Python files**

Run:

```powershell
rtk ruff check examples/webhook_quickstart.py tests/examples/test_webhook_quickstart.py
rtk ruff format --check examples/webhook_quickstart.py tests/examples/test_webhook_quickstart.py
```

Expected: both commands exit successfully with no lint or formatting changes
required.

- [ ] **Step 7: Commit the implementation**

Review the staged scope before committing because the worktree contains
unrelated user changes:

```powershell
rtk git status --short
rtk git add -- examples/webhook_quickstart.py tests/examples/test_webhook_quickstart.py
rtk git diff --cached --stat
rtk git commit -m "feat: verify webhook quickstart timestamps"
```

Expected: the staged diff contains exactly the quickstart example and its test
file, and the commit succeeds.
