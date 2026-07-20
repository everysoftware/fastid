# Webhook Receiver Examples Design

## Context

FastID now sends only Standard Webhooks authentication headers. The tutorial contains a short receiver fragment, but
`examples/` does not contain a complete webhook consumer that users can run or copy. A single example cannot remain
brief enough for a quick start while also teaching replay protection, concurrency, and durable idempotency.

FastID will provide three standalone FastAPI applications. Each file intentionally repeats signature verification so a
reader can copy it without importing another example or installing FastID as a library.

## Files and audiences

### `examples/webhook_quickstart.py`

The quick-start application is the shortest safe receiver. It requires `FASTID_WEBHOOK_SECRET` at startup, reads the
exact raw body, uses the three Standard Webhooks headers to verify the signature, parses JSON only after authentication,
logs the generic event, and returns `204 No Content`.

It demonstrates authentication but not replay protection or idempotency. It reads `webhook-id` and
`webhook-timestamp` only because they are signature inputs, without checking timestamp freshness or interpreting the
Webhook ID. A comment directs production consumers to the advanced examples before applying side effects.

### `examples/webhook_advanced.py`

The advanced application adds request-size enforcement, structural payload validation, timestamp freshness, explicit
error responses, and an asynchronous idempotency-store protocol. Its in-memory adapter uses an `asyncio.Lock` so
concurrent requests in one process cannot claim the same Webhook ID twice.

The adapter is intentionally labeled as a reference implementation: it is not shared across processes and loses state
on restart. The protocol boundary shows where a production consumer supplies durable storage without mixing database
setup into this example.

### `examples/webhook_sqlalchemy.py`

The SQLAlchemy application is a standalone alternative to the advanced example. It implements an equivalent claim,
complete, and release lifecycle with a table whose Webhook ID is unique. A duplicate insert is the atomic concurrency
boundary.

`WEBHOOK_DATABASE_URL` configures the database and defaults to a local SQLite file so the example is runnable without
external infrastructure. The example uses SQLAlchemy's async engine, async session factory, and `AsyncSession` for all
schema and claim operations; it does not bridge synchronous database work through a worker thread. The default driver
is `aiosqlite`, installed from Poetry's optional `examples` dependency group.

## Configuration

All three applications require a non-empty `FASTID_WEBHOOK_SECRET`. Startup fails with a clear message if it is absent.
Secrets beginning with `whsec_` contain base64-encoded key bytes. Plain-text secrets remain accepted for compatibility
with existing endpoints.

The advanced and SQLAlchemy applications use these fixed reference limits:

- maximum request body: 1 MiB;
- timestamp tolerance: 300 seconds.

The SQLAlchemy application additionally accepts `WEBHOOK_DATABASE_URL`, defaulting to
`sqlite+aiosqlite:///webhook-events.sqlite3`. Install its optional driver with
`poetry install --with examples`.

## Authentication

Each receiver reads:

- `webhook-id` as the stable Webhook ID and idempotency identifier;
- `webhook-timestamp` as an integer Unix timestamp;
- `webhook-signature` as one or more space-separated versioned signatures.

The expected `v1` signature is base64-encoded HMAC-SHA256 over the exact byte sequence
`webhook-id.webhook-timestamp.raw_body`. Verification compares signatures with `hmac.compare_digest`. The body is not
parsed or re-serialized before verification.

Unknown signature versions are ignored so a future FastID rotation can send old and new signatures together. A request
is authenticated when any supplied `v1` signature matches. The quick-start stops at this authentication check. The
advanced examples additionally parse the timestamp as an integer and reject messages outside the tolerance.

## Payload model

The examples are event-type agnostic. After signature verification, they require a JSON object with:

- `event.event_id`: the logical domain event UUID, independent of `webhook-id`;
- `event.event_type`: a non-empty string;
- `event.timestamp`: an integer;
- `data`: a JSON object.

They log the event ID and event type but do not dispatch business-specific handlers.

The quick-start keeps payload checks minimal to stay concise. The advanced examples validate the complete generic
envelope before claiming the event.

## Advanced request flow

1. Reject a declared `Content-Length` greater than 1 MiB.
2. Read the raw body and reject an actual body greater than 1 MiB.
3. Validate required headers, integer timestamp, timestamp tolerance, secret encoding, and HMAC.
4. Parse and validate the generic JSON envelope.
5. Atomically claim the Webhook ID from `webhook-id`.
6. If already claimed or completed, return `204` without processing it again.
7. Log receipt and mark the claim complete.
8. If processing raises, release the claim and return `500` so FastID retries.

The claim lifecycle prevents simultaneous duplicate processing in the demonstrated execution model. It does not promise
exactly-once side effects across a crash between the side effect and completion; production applications must make the
business change idempotent or commit an inbox record and business state in one transaction.

## Error responses

- `400 Bad Request`: missing or malformed webhook headers, stale timestamp in advanced examples, malformed JSON, or an
  invalid event envelope;
- `401 Unauthorized`: a well-formed request with no matching signature;
- `413 Content Too Large`: declared or actual body exceeds 1 MiB;
- `500 Internal Server Error`: processing or idempotency storage fails, allowing FastID to retry;
- `204 No Content`: a new event was accepted or a duplicate was already claimed.

Error bodies use FastAPI's normal JSON `detail` shape. Error messages do not include secrets, signatures, or raw body
contents.

## Testing

Tests import each standalone application with controlled environment variables and exercise it through FastAPI's test
client. Shared test-only helpers generate valid Standard Webhooks signatures; examples do not import those helpers.

Coverage includes:

- valid request acceptance for all three applications;
- exact-body signature tampering;
- missing, malformed, and non-matching signatures;
- stale timestamps;
- malformed JSON and invalid envelope fields;
- declared and actual oversized bodies in advanced applications;
- repeated delivery acknowledgement without repeated processing;
- concurrent claims against the in-memory adapter;
- SQLAlchemy duplicate claims and persistence across store instances.
- async SQLAlchemy schema creation, claim, completion, release, and engine disposal without thread-pool calls.

Ruff, mypy, focused example tests, and the complete project suite must pass.

## Documentation

The webhook tutorial will link to the quick-start, advanced, and SQLAlchemy files and describe their intended audiences.
The examples remain source files rather than embedded copies so documentation cannot drift from runnable code.
