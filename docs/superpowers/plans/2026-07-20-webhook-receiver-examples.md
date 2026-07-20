# Webhook Receiver Examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify FastID's webhook identifiers and provide three independently runnable FastAPI webhook receivers for quick-start, in-memory advanced, and SQLAlchemy-backed use cases.

**Architecture:** FastID models a configured destination as `WebhookEndpoint`, a delivered webhook as `WebhookDelivery`, and a domain event as `Event`. `WebhookDelivery.id` is the Webhook ID signed into `webhook-id`; `WebhookDelivery.endpoint_id` links to the endpoint; `event.event_id` remains independent. Every example contains its own Standard Webhooks verifier so it can be copied without importing FastID.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, Starlette TestClient, pytest, Ruff, mypy

## Global Constraints

- Use **Webhook Endpoint ID**, **Webhook ID**, and **Event ID** as the domain terms.
- Use concise contextual attributes: `WebhookDelivery.endpoint_id` and `WebhookDelivery.endpoint`.
- Use `webhook_id` internally and `webhook-id` externally for `WebhookDelivery.id`; do not use `message_id` or `delivery_id` aliases for this value.
- Treat `event.event_id` as independent from `webhook-id`; never compare them.
- Use only `webhook-id`, `webhook-timestamp`, and `webhook-signature` authentication headers.
- Verify `webhook-id.webhook-timestamp.raw_body` with HMAC-SHA256 before JSON parsing.
- Accept `v1,<base64>` signatures and `whsec_<base64>` secrets; retain plain-secret compatibility.
- Require `FASTID_WEBHOOK_SECRET` during FastAPI lifespan startup.
- The quick-start performs signature authentication only: no timestamp freshness, identifier-format, replay, or idempotency checks.
- Use a 300-second timestamp tolerance and a 1 MiB body limit in advanced examples only.
- Keep all three example files standalone; they must not import each other or `fastid.*`.
- Keep event processing generic: validate and log receipt, but do not dispatch event-specific handlers.
- Do not demonstrate a FastID application database in the quick-start or in-memory examples.
- Prefix every shell command with `rtk`.

## File structure

- `fastid/webhooks/models.py`: endpoint, delivery, and attempt persistence models.
- `fastid/apps/models.py`: application-to-webhook-endpoint relationship.
- `fastid/webhooks/repositories.py`: endpoint and delivery repositories/specifications.
- `fastid/database/uow.py`: repository attributes used by webhook use cases and workers.
- `fastid/webhooks/use_cases.py`: creates one delivery per matching endpoint.
- `fastid/webhooks/worker.py`: signs Webhook IDs and resolves endpoint relationships.
- `fastid/security/webhooks.py`: Standard Webhooks signing and verification helpers.
- `migrations/versions/2026_07_20_1200-5b2c8d7e9f10_rename_webhooks_to_endpoints.py`: lossless endpoint table, version table, column, constraint, and index renames.
- `examples/webhook_quickstart.py`: minimal authenticated receiver.
- `examples/webhook_advanced.py`: validated receiver with an async in-memory idempotency boundary.
- `examples/webhook_sqlalchemy.py`: validated receiver with durable SQLAlchemy claims.
- `tests/examples/webhook_helpers.py`: test-only signer and payload factory.
- `tests/examples/test_webhook_quickstart.py`: quick-start behavior and startup configuration.
- `tests/examples/test_webhook_advanced.py`: advanced validation, limits, duplicates, and concurrent claims.
- `tests/examples/test_webhook_sqlalchemy.py`: database claims, persistence, duplicates, and HTTP behavior.
- `docs/docs/tutorial/webhooks.md`: receiver contract and links to each runnable example.

---

### Task 1: Rename configured webhooks to webhook endpoints

**Files:**
- Create: `tests/webhooks/test_endpoint_models.py`
- Create: `migrations/versions/2026_07_20_1200-5b2c8d7e9f10_rename_webhooks_to_endpoints.py`
- Modify: `fastid/webhooks/models.py`
- Modify: `fastid/apps/models.py`
- Modify: `fastid/webhooks/repositories.py`
- Modify: `fastid/database/models.py`
- Modify: `fastid/database/versioning.py`
- Modify: `fastid/database/uow.py`
- Modify: `fastid/webhooks/use_cases.py`
- Modify: `fastid/webhooks/worker.py`
- Modify: `fastid/admin/views/settings.py`
- Modify: `fastid/admin/views/versioning.py`
- Modify: `tests/utils/webhooks.py`
- Modify: `tests/api/conftest.py`
- Modify: webhook API tests importing the persistence model under `tests/api/auth/`, `tests/api/profile/`, and `tests/api/webhooks/`

**Interfaces:**
- Produces: `WebhookEndpoint(VersionedEntity)` mapped to `webhook_endpoints`.
- Produces: `WebhookDelivery.endpoint_id: UUID` and `WebhookDelivery.endpoint: WebhookEndpoint`.
- Produces: `App.webhook_endpoints: list[WebhookEndpoint]`.
- Produces: `WebhookEndpointRepository`, `WebhookEndpointTypeSpecification`, and `WebhookDeliveryEndpointIDSpecification`.
- Preserves: all existing endpoint, delivery, and version row IDs during migration.

- [ ] **Step 1: Write the failing model-contract test**

Create `tests/webhooks/test_endpoint_models.py`:

```python
from fastid.apps.models import App
from fastid.webhooks.models import WebhookDelivery, WebhookEndpoint


def test_webhook_endpoint_and_delivery_mapping_names() -> None:
    assert WebhookEndpoint.__tablename__ == "webhook_endpoints"
    assert WebhookDelivery.__table__.c.endpoint_id.name == "endpoint_id"
    foreign_key = next(iter(WebhookDelivery.__table__.c.endpoint_id.foreign_keys))
    assert foreign_key.target_fullname == "webhook_endpoints.id"
    assert WebhookDelivery.endpoint.property.mapper.class_ is WebhookEndpoint
    assert App.webhook_endpoints.property.mapper.class_ is WebhookEndpoint
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
rtk proxy poetry run pytest tests/webhooks/test_endpoint_models.py -q
```

Expected: collection fails because `WebhookEndpoint` does not exist.

- [ ] **Step 3: Rename the ORM model and contextual attributes**

Implement these exact mappings in `fastid/webhooks/models.py` and `fastid/apps/models.py`:

```python
class WebhookEndpoint(VersionedEntity):
    __tablename__ = "webhook_endpoints"

    app_id: Mapped[UUID] = mapped_column(ForeignKey("apps.id"), index=True)
    type: Mapped[WebhookType]
    secret: Mapped[str] = mapped_column(default=generate_webhook_secret)
    url: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    disabled_at: Mapped[datetime.datetime | None]
    disabled_reason: Mapped[str | None]

    app: Mapped[App] = relationship(back_populates="webhook_endpoints")
    deliveries: Mapped[list[WebhookDelivery]] = relationship(back_populates="endpoint", cascade="delete")


class WebhookDelivery(Entity):
    __tablename__ = "webhook_deliveries"

    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("webhook_endpoints.id"), index=True)
    event_id: Mapped[UUID] = mapped_column(index=True)
    event_type: Mapped[WebhookType]
    payload: Mapped[dict[str, Any]]
    status: Mapped[WebhookDeliveryStatus] = mapped_column(default=WebhookDeliveryStatus.pending, index=True)
    attempt_count: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime.datetime] = mapped_column(index=True)
    leased_until: Mapped[datetime.datetime | None] = mapped_column(index=True)
    completed_at: Mapped[datetime.datetime | None]
    request: Mapped[dict[str, Any] | None]
    status_code: Mapped[int | None]
    response: Mapped[dict[str, Any] | None]
    error: Mapped[str | None]

    endpoint: Mapped[WebhookEndpoint] = relationship(back_populates="deliveries")
    attempts: Mapped[list[WebhookAttempt]] = relationship(back_populates="delivery", cascade="delete")
```

```python
class App(VersionedEntity):
    __tablename__ = "apps"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    client_id: Mapped[str] = mapped_column(default=uuid_hex, index=True)
    client_secret: Mapped[str] = mapped_column(default=uuid_hex)
    redirect_uris: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)

    webhook_endpoints: Mapped[list[WebhookEndpoint]] = relationship(back_populates="app", cascade="delete")
```

Apply these symbol mappings everywhere listed in **Files**:

```text
Webhook                         -> WebhookEndpoint
WebhookVersion                  -> WebhookEndpointVersion
WebhookRepository               -> WebhookEndpointRepository
WebhookTypeSpecification        -> WebhookEndpointTypeSpecification
WebhookDeliveryWebhookIDSpecification -> WebhookDeliveryEndpointIDSpecification
delivery.webhook_id             -> delivery.endpoint_id
delivery.webhook                -> delivery.endpoint
App.webhooks                    -> App.webhook_endpoints
```

Keep the payload schema `fastid.webhooks.schemas.Webhook` unchanged; it is not the persistence model.

- [ ] **Step 4: Update use-case and worker data flow**

Use endpoint terminology at the call sites:

```python
endpoint_page = await self.uow.webhook_endpoints.get_many(WebhookEndpointTypeSpecification(dto.type))
for endpoint in endpoint_page.items:
    delivery = WebhookDelivery(
        id=get_webhook_id(),
        endpoint_id=endpoint.id,
        event_id=event_id,
        event_type=dto.type,
        payload=payload,
        status=WebhookDeliveryStatus.pending,
        next_attempt_at=now,
    )
```

In the worker, use `joinedload(WebhookDelivery.endpoint)`, read `delivery.endpoint.url` and
`delivery.endpoint.secret`, load `uow.webhook_endpoints.get(delivery.endpoint_id)`, and cancel sibling deliveries with:

```python
WebhookDelivery.endpoint_id == endpoint.id
```

- [ ] **Step 5: Add the lossless Alembic rename migration**

Create `migrations/versions/2026_07_20_1200-5b2c8d7e9f10_rename_webhooks_to_endpoints.py` with:

```python
"""rename webhooks to endpoints

Revision ID: 5b2c8d7e9f10
Revises: a4e1d2c3b5f6
Create Date: 2026-07-20 12:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "5b2c8d7e9f10"
down_revision: str | None = "a4e1d2c3b5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UPGRADE_RENAMES = (
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhooks_pkey TO webhook_endpoints_pkey",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhooks_app_id_fkey TO webhook_endpoints_app_id_fkey",
    "ALTER INDEX webhooks_app_id_idx RENAME TO webhook_endpoints_app_id_idx",
    "ALTER TABLE webhook_endpoints_version RENAME CONSTRAINT webhooks_version_pkey TO webhook_endpoints_version_pkey",
    "ALTER INDEX webhooks_version_app_id_idx RENAME TO webhook_endpoints_version_app_id_idx",
    "ALTER INDEX webhooks_version_end_transaction_id_idx RENAME TO webhook_endpoints_version_end_transaction_id_idx",
    "ALTER INDEX webhooks_version_operation_type_idx RENAME TO webhook_endpoints_version_operation_type_idx",
    "ALTER INDEX webhooks_version_transaction_id_idx RENAME TO webhook_endpoints_version_transaction_id_idx",
    "ALTER TABLE webhook_deliveries RENAME CONSTRAINT webhook_deliveries_webhook_id_fkey TO webhook_deliveries_endpoint_id_fkey",
    "ALTER INDEX webhook_deliveries_webhook_id_idx RENAME TO webhook_deliveries_endpoint_id_idx",
)

DOWNGRADE_RENAMES = (
    "ALTER INDEX webhook_deliveries_endpoint_id_idx RENAME TO webhook_deliveries_webhook_id_idx",
    "ALTER TABLE webhook_deliveries RENAME CONSTRAINT webhook_deliveries_endpoint_id_fkey TO webhook_deliveries_webhook_id_fkey",
    "ALTER INDEX webhook_endpoints_version_transaction_id_idx RENAME TO webhooks_version_transaction_id_idx",
    "ALTER INDEX webhook_endpoints_version_operation_type_idx RENAME TO webhooks_version_operation_type_idx",
    "ALTER INDEX webhook_endpoints_version_end_transaction_id_idx RENAME TO webhooks_version_end_transaction_id_idx",
    "ALTER INDEX webhook_endpoints_version_app_id_idx RENAME TO webhooks_version_app_id_idx",
    "ALTER TABLE webhook_endpoints_version RENAME CONSTRAINT webhook_endpoints_version_pkey TO webhooks_version_pkey",
    "ALTER INDEX webhook_endpoints_app_id_idx RENAME TO webhooks_app_id_idx",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhook_endpoints_app_id_fkey TO webhooks_app_id_fkey",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhook_endpoints_pkey TO webhooks_pkey",
)


def upgrade() -> None:
    op.rename_table("webhooks", "webhook_endpoints")
    op.rename_table("webhooks_version", "webhook_endpoints_version")
    op.alter_column("webhook_deliveries", "webhook_id", new_column_name="endpoint_id")
    for statement in UPGRADE_RENAMES:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_RENAMES:
        op.execute(statement)
    op.alter_column("webhook_deliveries", "endpoint_id", new_column_name="webhook_id")
    op.rename_table("webhook_endpoints_version", "webhooks_version")
    op.rename_table("webhook_endpoints", "webhooks")
```

This migration must rename in place; it must not recreate or copy tables.

- [ ] **Step 6: Verify the endpoint rename**

Run:

```powershell
rtk proxy poetry run pytest tests/webhooks/test_endpoint_models.py tests/api/webhooks tests/api/auth tests/api/profile -q
rtk proxy poetry run ruff check fastid tests/webhooks/test_endpoint_models.py tests/api
rtk proxy poetry run mypy fastid tests/webhooks/test_endpoint_models.py
rtk rg -n "WebhookDelivery\.webhook_id|WebhookDelivery\.webhook\b|from fastid\.webhooks\.models import Webhook\b|class Webhook\(" fastid tests
```

Expected: tests and static checks pass; the final search reports only the intentionally unchanged payload schema if it
matches at all.

- [ ] **Step 7: Commit the endpoint rename**

```powershell
rtk proxy git add fastid migrations/versions/2026_07_20_1200-5b2c8d7e9f10_rename_webhooks_to_endpoints.py tests
rtk proxy git commit -m "refactor: name webhook endpoints explicitly"
```

---

### Task 2: Make Webhook ID the signed delivery identifier

**Files:**
- Modify: `tests/api/webhooks/test_worker_delivery.py`
- Modify: `tests/security/test_webhooks.py`
- Modify: `tests/mocks.py`
- Modify: `fastid/security/webhooks.py`
- Modify: `fastid/webhooks/worker.py`

**Interfaces:**
- Produces: `generate_standard_signature(body: bytes, webhook_id: str, timestamp: int, secret_key: str) -> str`.
- Produces: `generate_delivery_headers(body: bytes, webhook_id: str, timestamp: int, secret_key: str) -> dict[str, str]`.
- Guarantees: `headers["webhook-id"] == str(WebhookDelivery.id)` and is independent of `event.event_id`.

- [ ] **Step 1: Write the failing sender-semantics assertion**

In the successful worker delivery test, add:

```python
headers = sender.requests[0].headers
assert headers["webhook-id"] == str(delivery.id)
assert headers["webhook-id"] != str(delivery.event_id)
```

- [ ] **Step 2: Run the focused test and verify RED**

```powershell
rtk proxy poetry run pytest tests/api/webhooks/test_worker_delivery.py::test_worker_records_delivery_outcome -q
```

Expected: the first assertion fails while the worker still signs the Event ID.

- [ ] **Step 3: Use `webhook_id` consistently in signing code**

Implement:

```python
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
```

`verify_standard_headers()` must also name the parsed header value `webhook_id`. The worker passes
`str(delivery.id)` to `generate_delivery_headers()`.

- [ ] **Step 4: Verify GREEN and commit**

```powershell
rtk proxy poetry run pytest tests/api/webhooks/test_worker_delivery.py tests/security/test_webhooks.py -q
rtk proxy poetry run ruff check fastid/security/webhooks.py fastid/webhooks/worker.py tests/security tests/api/webhooks/test_worker_delivery.py
rtk proxy poetry run mypy fastid/security/webhooks.py fastid/webhooks/worker.py
rtk proxy git add fastid/security/webhooks.py fastid/webhooks/worker.py tests/security/test_webhooks.py tests/api/webhooks/test_worker_delivery.py tests/mocks.py
rtk proxy git commit -m "refactor: separate webhook and event identifiers"
```

---

### Task 3: Align the quick-start receiver with signature-only verification

**Files:**
- Modify: `tests/examples/webhook_helpers.py`
- Modify: `tests/examples/test_webhook_quickstart.py`
- Modify: `examples/webhook_quickstart.py`

**Interfaces:**
- Produces: `app: FastAPI`.
- Produces: `verify_signature(body: bytes, webhook_id: str, timestamp: str, signatures: str, secret: str) -> bool`.
- Endpoint: `POST /fastid-webhooks -> 204 | 400 | 401`.

- [ ] **Step 1: Write the quick-start contract test**

Replace freshness and ID-equality tests with:

```python
def test_treats_webhook_id_and_timestamp_as_opaque_signature_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = compact_json(payload())
    headers = headers_for(body, "opaque-webhook-id", timestamp="opaque-timestamp")
    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)
    assert response.status_code == 204
```

Ensure `signed_request()` generates a Webhook ID independently of the payload Event ID.

- [ ] **Step 2: Run the quick-start tests and verify RED**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_quickstart.py -q
```

Expected: the opaque timestamp or independent Webhook ID is rejected by the old implementation.

- [ ] **Step 3: Implement signature-only behavior and concise naming**

Read required headers as strings and authenticate only this input:

```python
webhook_id = _required_header(request, "webhook-id")
timestamp = _required_header(request, "webhook-timestamp")
signatures = _required_header(request, "webhook-signature")
if not verify_signature(body, webhook_id, timestamp, signatures, request.app.state.webhook_secret):
    raise HTTPException(status_code=401, detail="Invalid webhook signature")
```

Do not parse the timestamp, validate the Webhook ID format, compare it with `event.event_id`, or add an idempotency
store. Rename every `message_id` local and parameter to `webhook_id`.

- [ ] **Step 4: Verify GREEN and commit**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_quickstart.py -q
rtk proxy poetry run ruff check examples/webhook_quickstart.py tests/examples
rtk proxy poetry run mypy examples/webhook_quickstart.py tests/examples
rtk proxy git add examples/webhook_quickstart.py tests/examples/test_webhook_quickstart.py tests/examples/webhook_helpers.py
rtk proxy git commit -m "docs: simplify webhook quick-start verification"
```

---

### Task 4: Align advanced in-memory idempotency with Webhook ID

**Files:**
- Modify: `tests/examples/test_webhook_advanced.py`
- Modify: `examples/webhook_advanced.py`

**Interfaces:**
- Produces: `IdempotencyStore` methods `claim(webhook_id)`, `complete(webhook_id)`, and `release(webhook_id)`.
- Produces: `InMemoryIdempotencyStore` implementing that protocol with one `asyncio.Lock`.
- Produces: `create_app(store: IdempotencyStore | None = None, processor: EventProcessor = process_event) -> FastAPI`.

- [ ] **Step 1: Write independent-ID and replay tests**

Use an independently generated `webhook-id`, assert a repeated signed request is processed once, and assert stale
timestamps still return `400`:

```python
assert headers["webhook-id"] != value["event"]["event_id"]
assert first.status_code == 204
assert duplicate.status_code == 204
assert processed_event_ids == [value["event"]["event_id"]]
```

Keep concurrent claim and release/retry coverage, but name all store keys `webhook_id`.

- [ ] **Step 2: Run the advanced tests and verify RED**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_advanced.py -q
```

Expected: the old header/payload equality check or old API terminology fails.

- [ ] **Step 3: Implement Webhook-ID idempotency**

Use this protocol and data flow:

```python
class IdempotencyStore(Protocol):
    async def claim(self, webhook_id: str) -> bool: ...
    async def complete(self, webhook_id: str) -> None: ...
    async def release(self, webhook_id: str) -> None: ...
```

`_validated_event()` returns `(event, webhook_id)` without comparing identifiers. `_receive_webhook()` atomically
claims `webhook_id`, acknowledges a duplicate with `204`, completes it after processing, and releases it on failure.
Retain integer timestamp parsing, 300-second freshness, signature verification, Pydantic validation, and body limits.
Rename log fields from `message_id` to `webhook_id`.

- [ ] **Step 4: Verify GREEN and commit**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_advanced.py -q
rtk proxy poetry run ruff check examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
rtk proxy poetry run mypy examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
rtk proxy git add examples/webhook_advanced.py tests/examples/test_webhook_advanced.py
rtk proxy git commit -m "docs: use webhook IDs for receiver idempotency"
```

---

### Task 5: Add the standalone SQLAlchemy receiver

**Files:**
- Create: `examples/webhook_sqlalchemy.py`
- Modify: `tests/examples/test_webhook_sqlalchemy.py`

**Interfaces:**
- Produces: `WebhookReceipt` with unique string `webhook_id`, `status`, `created_at`, and `updated_at` columns.
- Produces: `SQLAlchemyIdempotencyStore(engine: Engine)` with synchronous `claim`, `complete`, and `release` methods.
- Produces: `create_app(database_url: str | None = None, processor: EventProcessor = process_event) -> FastAPI`.
- Endpoint: `POST /fastid-webhooks -> 204 | 400 | 401 | 413 | 500`.

- [ ] **Step 1: Finish the failing SQLAlchemy store tests**

Use `tmp_path / "webhooks.sqlite3"` and two store instances:

```python
def test_claim_persists_across_store_instances(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'webhooks.sqlite3'}"
    first = SQLAlchemyIdempotencyStore(create_store_engine(database_url))
    second = SQLAlchemyIdempotencyStore(create_store_engine(database_url))
    first.create_schema()
    assert first.claim("webhook-1")
    first.complete("webhook-1")
    assert not second.claim("webhook-1")
```

Add concurrent claim, release/reclaim, valid/duplicate HTTP delivery, processing-failure retry, and parameterized
`400`/`401`/`413` coverage. Use independent Webhook IDs and Event IDs throughout.

- [ ] **Step 2: Run the SQLAlchemy tests and verify RED**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_sqlalchemy.py -q
```

Expected: collection fails because `examples.webhook_sqlalchemy` does not exist.

- [ ] **Step 3: Implement the durable claim store**

Create a local declarative model:

```python
def utc_now() -> datetime:
    return datetime.now(UTC)


class WebhookReceipt(Base):
    __tablename__ = "webhook_receipts"

    webhook_id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)
```

`claim(webhook_id)` inserts `processing` in `Session.begin()` and returns `False` on `IntegrityError`.
`complete(webhook_id)` updates the row to `completed`. `release(webhook_id)` deletes only a `processing` row.
`create_schema()` calls `Base.metadata.create_all(engine)`. `create_store_engine()` sets
`connect_args={"check_same_thread": False}` only for SQLite.

- [ ] **Step 4: Implement the standalone FastAPI receiver**

Repeat the advanced example's verifier, envelope, freshness, size, and error behavior without importing another example
or `fastid.*`. Lifespan selects the explicit argument, then `WEBHOOK_DATABASE_URL`, then
`sqlite:///webhook-events.sqlite3`; it creates the schema and disposes the engine at shutdown. Run every synchronous
store call through `starlette.concurrency.run_in_threadpool`:

```python
claimed = await run_in_threadpool(store.claim, webhook_id)
if not claimed:
    return Response(status_code=204)
try:
    await processor(event)
    await run_in_threadpool(store.complete, webhook_id)
except Exception as exc:
    await run_in_threadpool(store.release, webhook_id)
    raise HTTPException(status_code=500, detail="Webhook processing failed") from exc
return Response(status_code=204)
```

- [ ] **Step 5: Verify GREEN and commit**

```powershell
rtk proxy poetry run pytest tests/examples/test_webhook_sqlalchemy.py -q
rtk proxy poetry run ruff check examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
rtk proxy poetry run mypy examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
rtk proxy git add examples/webhook_sqlalchemy.py tests/examples/test_webhook_sqlalchemy.py
rtk proxy git commit -m "docs: add SQLAlchemy webhook receiver example"
```

---

### Task 6: Update the tutorial and verify the complete feature

**Files:**
- Modify: `docs/docs/tutorial/webhooks.md`
- Modify: `docs/superpowers/plans/2026-07-20-standard-webhook-headers.md`
- Modify: `docs/superpowers/plans/2026-07-20-webhook-receiver-examples.md`

**Interfaces:**
- Consumes: the endpoint terminology and all three runnable receiver paths.
- Produces: one discoverable progression from signature-only quick-start to production-oriented references.

- [ ] **Step 1: Remove obsolete terminology**

Use `Webhook ID` in prose and `webhook_id` in code. Replace references to the configured `Webhook` entity with
`Webhook Endpoint` where the distinction matters. Verify with:

```powershell
rtk rg -ni "message[ _-]?id|WebhookDelivery\.webhook_id|WebhookDelivery\.webhook\b|stable event id|header/payload.*match" docs examples fastid tests
```

Expected: no obsolete terminology remains except historical migration descriptions that explicitly name an old schema.

- [ ] **Step 2: Add the receiver progression to the tutorial**

Document:

```markdown
Runnable receiver examples are available for different integration stages:

- [`webhook_quickstart.py`](../../../examples/webhook_quickstart.py) verifies a signature and logs the event.
- [`webhook_advanced.py`](../../../examples/webhook_advanced.py) adds freshness checks, validation, limits, and an
  in-memory Webhook-ID idempotency boundary.
- [`webhook_sqlalchemy.py`](../../../examples/webhook_sqlalchemy.py) persists atomic Webhook-ID claims with SQLAlchemy.

The quick-start authenticates the request but does not provide replay protection or idempotency. The in-memory example
is a concurrency reference, not durable storage. Use the SQLAlchemy example or another shared persistent store before
applying non-idempotent production side effects.
```

- [ ] **Step 3: Run focused verification**

```powershell
rtk proxy poetry run pytest tests/security/test_webhooks.py tests/api/webhooks tests/webhooks tests/examples -q
rtk proxy poetry run ruff check fastid examples tests
rtk proxy poetry run mypy fastid examples tests/examples
rtk proxy poetry run codespell examples tests/examples docs/docs/tutorial/webhooks.md docs/glossary.md
```

Expected: all focused tests and static checks pass.

- [ ] **Step 4: Run complete project verification**

```powershell
rtk proxy poetry run pytest -q
rtk proxy poetry run ruff check .
rtk proxy poetry run mypy fastid examples tests/examples
rtk proxy git diff --check
rtk proxy git status --short
```

Expected: all tests and static checks pass; only the planned final documentation changes remain uncommitted.

- [ ] **Step 5: Commit documentation and confirm history**

```powershell
rtk proxy git add docs examples tests fastid migrations
rtk proxy git commit -m "docs: finish webhook receiver examples"
rtk proxy git status --short
rtk proxy git log -8 --oneline
```

Expected: the worktree is clean and the endpoint, identifier, receiver, and tutorial commits are at the top of
`feat/enhance-webhooks`.
