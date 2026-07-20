# Standard Webhook Headers Design

## Context

FastID currently sends two independent webhook authentication protocols on every delivery:

- legacy configurable `X-Webhook-*` headers, whose signature covers a re-serialized JSON payload;
- fixed Standard Webhooks headers, whose signature covers the exact raw request body.

The legacy `X-Webhook-Id` identifies a delivery, while the standard `webhook-id` identifies the logical event and remains
stable across retries. Keeping both protocols makes the consumer contract ambiguous and complicates the webhook
examples.

The repository has no production caller of the legacy signing or verification functions. The legacy protocol remains
only in the delivery-header composition, configuration, tests, and a compatibility note in the webhook tutorial. There
are no tagged releases establishing a published compatibility requirement.

## Decision

FastID will expose only the Standard Webhooks header family:

- `webhook-id`: stable logical event ID;
- `webhook-timestamp`: Unix timestamp for the delivery attempt;
- `webhook-signature`: one or more space-separated `v1,<base64 HMAC-SHA256>` signatures.

The signed content remains the exact byte sequence
`webhook-id.webhook-timestamp.raw_body`. Endpoint secrets retain the `whsec_` prefix and base64-encoded key material.

## Code changes

`generate_delivery_headers()` will directly construct the standard headers plus `Content-Type` and `User-Agent`. It
will no longer accept or use a separately generated delivery ID for authentication.

The following legacy API will be removed:

- `generate_headers()`;
- `generate_signature()`;
- `verify_headers()`;
- the `SignatureAlgorithm` enum and algorithm lookup table;
- configurable legacy ID, timestamp, and signature header settings.

`generate_standard_signature()`, `verify_standard_headers()`, payload serialization, timestamp validation, and secret
generation remain the supported implementation.

All callers, tests, and documentation will be updated to use the single protocol. The delivery database ID remains an
internal identifier and is not sent as an authentication header.

## Request flow

For each delivery attempt, the worker serializes the payload once, generates a timestamp, and signs the stable event ID,
timestamp, and exact serialized bytes. The sender transmits those same bytes and the generated standard headers.

Consumers read the raw body, validate timestamp freshness, calculate the expected HMAC over the raw bytes, compare the
signature in constant time, and only then parse JSON. Consumers use `webhook-id` as the idempotency key.

## Compatibility

This is an intentional breaking change for consumers that verify `X-Webhook-*`. Because the repository has no tagged
release and documentation already directs new integrations to Standard Webhooks, FastID will remove the legacy path
without a deprecation period.

No payload fields, delivery retry behavior, endpoint secrets, or persisted delivery records change.

## Error handling

The sender continues treating header generation errors as programming or configuration failures. Consumer-side
verification continues returning `False` for missing headers, malformed timestamps, stale timestamps, and signature
mismatches. An invalid `whsec_` value continues raising `ValueError` so configuration errors are distinguishable from
untrusted requests.

## Verification

Tests will establish that:

- generated deliveries contain only the standard authentication headers;
- signatures authenticate the exact UTF-8 body;
- header lookup is case-insensitive;
- body changes, wrong secrets, stale timestamps, and malformed headers fail verification;
- the worker passes valid standard headers to the sender;
- no legacy header settings, helpers, or documentation remain.

The focused webhook security and worker tests will run first, followed by linting and the broader test suite where
practical.

## Follow-up

After this change is verified, FastID will add three standalone webhook receiver examples: a quick-start receiver, an
advanced receiver with an idempotency-store abstraction, and a SQLAlchemy-backed receiver. Their design and
implementation remain separate from this prerequisite cleanup.
