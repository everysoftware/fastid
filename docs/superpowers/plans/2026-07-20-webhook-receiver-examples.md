# Webhook Receiver Examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three independently runnable FastAPI webhook receivers for quick-start, in-memory advanced, and SQLAlchemy-backed use cases.

**Architecture:** Every example contains its own Standard Webhooks verifier so it can be copied independently. The quick-start authenticates and logs generic events; the advanced examples add a claim/complete/release idempotency lifecycle, implemented first with a locked in-memory store and then with a SQLAlchemy table.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Starlette TestClient, pytest, Ruff, mypy

## Global Constraints

- Use only `webhook-id`, `webhook-timestamp`, and `webhook-signature`.
- Verify `webhook-id.webhook-timestamp.raw_body` with HMAC-SHA256 before JSON parsing.
- Accept `v1,<base64>` signatures and `whsec_<base64>` secrets; retain plain-secret compatibility.
- Require `FASTID_WEBHOOK_SECRET` during FastAPI lifespan startup.
- Use a 300-second timestamp tolerance and a 1 MiB advanced-example body limit.
- Keep all three example files standalone; they must not import each other or `fastid.*`.
- Keep event processing generic: validate and log receipt, but do not dispatch event-specific handlers.
- Prefix every shell command with `rtk`.

## File structure

- `examples/webhook_quickstart.py`: minimal authenticated receiver.
- `examples/webhook_advanced.py`: validated receiver with an async in-memory idempotency boundary.
- `examples/webhook_sqlalchemy.py`: validated receiver with durable SQLAlchemy claims.
- `tests/examples/webhook_helpers.py`: test-only signer and payload factory.
- `tests/examples/test_webhook_quickstart.py`: quick-start behavior and startup configuration.
- `tests/examples/test_webhook_advanced.py`: advanced validation, limits, duplicates, and concurrent claims.
- `tests/examples/test_webhook_sqlalchemy.py`: database claims, persistence, duplicates, and HTTP behavior.
- `docs/docs/tutorial/webhooks.md`: links to each runnable example and explains the audience.

---

### Task 1: Quick-start receiver

**Files:**
- Create: `tests/examples/__init__.py`
- Create: `tests/examples/webhook_helpers.py`
- Create: `tests/examples/test_webhook_quickstart.py`
- Create: `examples/webhook_quickstart.py`

**Interfaces:**
- Produces: `app: FastAPI`
- Produces: `verify_signature(body: bytes, webhook_id: str, timestamp: int, signatures: str, secret: str) -> bool`
- Endpoint: `POST /fastid-webhooks -> 204 | 400 | 401`

- [ ] **Step 1: Add a test-only Standard Webhooks signer**

Create `tests/examples/__init__.py` as an empty file. Create `tests/examples/webhook_helpers.py` with:

```python
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


def signed_request(value: dict[str, Any], secret: str = SECRET) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()
    event_id = str(value["event"]["event_id"])
    timestamp = int(time.time())
    key = base64.b64decode(secret.removeprefix("whsec_"), validate=True)
    signed = b".".join((event_id.encode(), str(timestamp).encode(), body))
    signature = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    return body, {
        "webhook-id": event_id,
        "webhook-timestamp": str(timestamp),
        "webhook-signature": f"v1,{signature}",
        "content-type": "application/json",
    }
```

- [ ] **Step 2: Write failing quick-start HTTP tests**

Create `tests/examples/test_webhook_quickstart.py` with tests that use `monkeypatch.setenv`, `TestClient`, and
`signed_request()` to assert:

```python
def test_accepts_valid_webhook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())
    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)
    assert response.status_code == 204
    assert response.content == b""


def test_requires_secret_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FASTID_WEBHOOK_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="FASTID_WEBHOOK_SECRET is required"), TestClient(app):
        pass


def test_rejects_tampered_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())
    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body + b" ", headers=headers)
    assert response.status_code == 401
```

Add separate tests for missing headers, a non-integer timestamp, a timestamp older than 300 seconds, malformed JSON,
an invalid envelope, and a header/payload event-ID mismatch. Assert `400` for each.

- [ ] **Step 3: Run quick-start tests and verify RED**

```powershell
rtk pytest tests/examples/test_webhook_quickstart.py -q
```

Expected: collection fails because `examples.webhook_quickstart` does not exist.

- [ ] **Step 4: Implement the standalone quick-start application**

Create `examples/webhook_quickstart.py` with:

- a FastAPI lifespan that reads and validates `FASTID_WEBHOOK_SECRET` into `app.state.webhook_secret`;
- `_secret_bytes()` supporting prefixed and plain secrets;
- `verify_signature()` that ignores unknown versions and constant-time compares every `v1` candidate;
- `POST /fastid-webhooks`, which reads the raw body, validates headers and timestamp, verifies before parsing JSON,
  validates `event.event_id`, `event.event_type`, and `data`, requires ID equality, logs the generic receipt, and returns
  `Response(status_code=204)`;
- `HTTPException(400, ...)` for malformed requests and `HTTPException(401, "Invalid webhook signature")` for a
  non-matching signature;
- a production-idempotency warning immediately above the log call;
- `if __name__ == "__main__": uvicorn.run("examples.webhook_quickstart:app", host="127.0.0.1", port=8000)`.

Use this exact signature input:

```python
signed = b".".join((webhook_id.encode(), str(timestamp).encode(), body))
expected = base64.b64encode(hmac.new(_secret_bytes(secret), signed, hashlib.sha256).digest()).decode()
return any(
    version == "v1" and hmac.compare_digest(value, expected)
    for signature in signatures.split()
    if "," in signature
    for version, value in (signature.split(",", 1),)
)
```

- [ ] **Step 5: Verify GREEN and static correctness**

```powershell
rtk pytest tests/examples/test_webhook_quickstart.py -q
rtk ruff check examples/webhook_quickstart.py tests/examples
rtk mypy examples/webhook_quickstart.py tests/examples
```

Expected: all checks pass.

- [ ] **Step 6: Commit**

```powershell
rtk git add examples/webhook_quickstart.py tests/examples
rtk git commit -m "docs: add webhook quick-start example"
```

---

### Task 2: Advanced in-memory receiver

**Files:**
- Create: `tests/examples/test_webhook_advanced.py`
- Create: `examples/webhook_advanced.py`

**Interfaces:**
- Produces: `IdempotencyStore(Protocol)` with async `claim(event_id) -> bool`, `complete(event_id) -> None`, and
  `release(event_id) -> None`.
- Produces: `InMemoryIdempotencyStore` implementing that protocol with one `asyncio.Lock`.
- Produces: `create_app(store: IdempotencyStore | None = None, processor: EventProcessor = process_event) -> FastAPI`.
- Endpoint: `POST /fastid-webhooks -> 204 | 400 | 401 | 413 | 500`.

- [ ] **Step 1: Write failing store and HTTP tests**

Create `tests/examples/test_webhook_advanced.py`. Test the wished-for API directly:

```python
async def test_concurrent_claim_has_one_winner() -> None:
    store = InMemoryIdempotencyStore()
    results = await asyncio.gather(*(store.claim("event-1") for _ in range(20)))
    assert results.count(True) == 1
    assert results.count(False) == 19


async def test_release_allows_retry() -> None:
    store = InMemoryIdempotencyStore()
    assert await store.claim("event-1")
    await store.release("event-1")
    assert await store.claim("event-1")
```

Use a recording async processor injected through `create_app()` and assert a repeated signed delivery returns `204`
twice but records one call. Add tests for declared and actual bodies over `MAX_BODY_BYTES`, invalid Pydantic envelope data,
ID mismatch, and a raising processor that returns `500` and can be retried successfully.

- [ ] **Step 2: Run advanced tests and verify RED**

```powershell
rtk pytest tests/examples/test_webhook_advanced.py -q
```

Expected: collection fails because `examples.webhook_advanced` does not exist.

- [ ] **Step 3: Implement the advanced standalone application**

Create `examples/webhook_advanced.py` with:

```python
MAX_BODY_BYTES = 1024 * 1024
ClaimStatus = Literal["processing", "completed"]
EventProcessor = Callable[["WebhookEnvelope"], Awaitable[None]]


class EventMetadata(BaseModel):
    event_id: UUID
    event_type: str = Field(min_length=1)
    timestamp: int


class WebhookEnvelope(BaseModel):
    event: EventMetadata
    data: dict[str, Any]


class IdempotencyStore(Protocol):
    async def claim(self, event_id: str) -> bool: ...
    async def complete(self, event_id: str) -> None: ...
    async def release(self, event_id: str) -> None: ...
```

`InMemoryIdempotencyStore` must guard a `dict[str, ClaimStatus]` with one lock. `claim()` inserts `processing` only when
absent, `complete()` changes an existing claim to `completed`, and `release()` removes only a `processing` claim.

Repeat the complete verification implementation from the quick-start file. `create_app()` must enforce both declared
and actual body length, validate with `WebhookEnvelope.model_validate_json(body)`, compare the normalized UUID to
`webhook-id`, claim before calling the processor, acknowledge duplicates, complete success, and release then raise
`HTTPException(500, "Webhook processing failed")` on processing/storage errors. The default processor logs the event.

Add the same direct `uvicorn.run()` entry point on port 8000.

- [ ] **Step 4: Verify GREEN and static correctness**

```powershell
rtk pytest tests/examples/test_webhook_advanced.py -q
rtk ruff check examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
rtk mypy examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
```

Expected: all checks pass.

- [ ] **Step 5: Commit**

```powershell
rtk git add examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
rtk git commit -m "docs: add advanced webhook receiver example"
```

---

### Task 3: SQLAlchemy-backed receiver

**Files:**
- Create: `tests/examples/test_webhook_sqlalchemy.py`
- Create: `examples/webhook_sqlalchemy.py`

**Interfaces:**
- Produces: `WebhookReceipt` with unique string `event_id`, `status`, `created_at`, and `updated_at` columns.
- Produces: `SQLAlchemyIdempotencyStore(engine: Engine)` with synchronous `claim`, `complete`, and `release` methods.
- Produces: `create_app(database_url: str | None = None, processor: EventProcessor = process_event) -> FastAPI`.
- Endpoint: `POST /fastid-webhooks -> 204 | 400 | 401 | 413 | 500`.

- [ ] **Step 1: Write failing SQLAlchemy store and HTTP tests**

Create `tests/examples/test_webhook_sqlalchemy.py`. Use `tmp_path / "webhooks.sqlite3"` and two engines/store instances.
Assert:

```python
def test_claim_persists_across_store_instances(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'webhooks.sqlite3'}"
    first = SQLAlchemyIdempotencyStore(create_store_engine(database_url))
    second = SQLAlchemyIdempotencyStore(create_store_engine(database_url))
    first.create_schema()
    assert first.claim("event-1")
    first.complete("event-1")
    assert not second.claim("event-1")
```

Add a concurrent claim test through `asyncio.to_thread`, a release/reclaim test, valid/duplicate HTTP delivery with a
recording processor, a processing-failure retry test, and one parameterized test proving the SQLAlchemy app returns the
same `400`, `401`, and `413` classes as the advanced app.

- [ ] **Step 2: Run SQLAlchemy tests and verify RED**

```powershell
rtk pytest tests/examples/test_webhook_sqlalchemy.py -q
```

Expected: collection fails because `examples.webhook_sqlalchemy` does not exist.

- [ ] **Step 3: Implement the standalone SQLAlchemy application**

Create `examples/webhook_sqlalchemy.py` with a local `DeclarativeBase`, `WebhookReceipt`, and
`SQLAlchemyIdempotencyStore`. `create_store_engine(database_url)` must set `check_same_thread=False` only for SQLite.

Use `Session.begin()` transactions. `claim()` inserts status `processing`, flushes, and returns `False` on
`IntegrityError`. `complete()` updates the matching row to `completed`. `release()` deletes only a `processing` row.
`create_schema()` calls `Base.metadata.create_all(engine)`.

Repeat the advanced file's signature, size, and envelope validation so this file remains standalone. FastAPI lifespan
must require `FASTID_WEBHOOK_SECRET`, select the explicit argument or `WEBHOOK_DATABASE_URL` or
`sqlite:///webhook-events.sqlite3`, create the engine/store/schema, and dispose the engine at shutdown.

Run every synchronous store call through `starlette.concurrency.run_in_threadpool`. A duplicate returns `204`; success
completes; failure releases and returns `500`. Add the direct uvicorn entry point.

- [ ] **Step 4: Verify GREEN and static correctness**

```powershell
rtk pytest tests/examples/test_webhook_sqlalchemy.py -q
rtk ruff check examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
rtk mypy examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
```

Expected: all checks pass.

- [ ] **Step 5: Commit**

```powershell
rtk git add examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
rtk git commit -m "docs: add SQLAlchemy webhook receiver example"
```

---

### Task 4: Tutorial links and final verification

**Files:**
- Modify: `docs/docs/tutorial/webhooks.md`

**Interfaces:**
- Consumes: all three runnable example paths.
- Produces: one discoverable progression from quick-start to production-oriented references.

- [ ] **Step 1: Add example links to the tutorial**

After the existing signature-verification fragment, add:

```markdown
Runnable receiver examples are available for different integration stages:

- [`webhook_quickstart.py`](../../../examples/webhook_quickstart.py) verifies and logs an event with minimal setup.
- [`webhook_advanced.py`](../../../examples/webhook_advanced.py) adds validation and an in-memory idempotency boundary.
- [`webhook_sqlalchemy.py`](../../../examples/webhook_sqlalchemy.py) persists atomic event claims with SQLAlchemy.

The in-memory example is a concurrency reference, not durable storage. Use the SQLAlchemy example or another shared,
persistent idempotency store before applying non-idempotent production side effects.
```

- [ ] **Step 2: Run focused example verification**

```powershell
rtk pytest tests/examples -q
rtk ruff check examples tests/examples
rtk mypy examples tests/examples
rtk codespell examples tests/examples docs/docs/tutorial/webhooks.md
```

Expected: all checks pass.

- [ ] **Step 3: Run the complete project verification**

```powershell
rtk pytest -q
rtk ruff check .
rtk mypy fastid examples tests/examples
rtk git diff --check
rtk git status --short
```

Expected: all tests and static checks pass; only the tutorial is pending before the final commit.

- [ ] **Step 4: Commit documentation and confirm history**

```powershell
rtk git add docs/docs/tutorial/webhooks.md
rtk git commit -m "docs: link webhook receiver examples"
rtk git status --short
rtk git log -5 --oneline
```

Expected: the worktree is clean and the four example commits are at the top of `feat/enhance-webhooks`.
