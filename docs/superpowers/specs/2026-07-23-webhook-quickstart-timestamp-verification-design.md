# Webhook Quickstart Timestamp Verification

## Goal

Protect the `webhook_quickstart` receiver from replayed webhook requests by
validating the signed `webhook-timestamp` header before accepting the request.

## Behavior

- The timestamp header must contain an integer Unix timestamp in seconds.
- The timestamp must be within 300 seconds of the receiver's current time.
- Timestamps more than 300 seconds in the past or future are rejected with
  HTTP 400 and `Webhook timestamp is outside the allowed tolerance`.
- Non-integer timestamp values are rejected with HTTP 400 and
  `Invalid webhook-timestamp header`.
- Timestamp validation occurs before signature validation.
- The original timestamp header value remains part of the signed message, so
  existing valid webhook signatures continue to verify.
- Invalid signatures continue to return HTTP 401.

## Implementation

Add a `TIMESTAMP_TOLERANCE_SECONDS = 300` constant and import `time` in
`examples/webhook_quickstart.py`. In `receive_webhook`, parse the required
timestamp header as an integer, reject malformed values, compare it with
`int(time.time())`, and reject timestamps outside the tolerance before calling
`verify_signature`.

The check stays inline to preserve the quickstart's linear, copyable structure
and mirrors the established behavior in `examples/webhook_advanced.py`.

## Testing

Update `tests/examples/test_webhook_quickstart.py` using the existing signed
request helpers:

- Keep the valid-webhook test as coverage for a current signed timestamp.
- Replace the test that treats timestamps as opaque with a malformed-timestamp
  rejection test.
- Add rejection tests for signed timestamps older and newer than the allowed
  tolerance.
- Assert HTTP 400 and the relevant error detail for timestamp failures.

Tests will be written and observed failing before the example is changed, then
the focused example tests and the broader relevant test suite will be run.

## Scope

This change affects only the quickstart example and its tests. It does not
change FastID's webhook sender, payload schema, signature format, advanced
receiver, or idempotency behavior.
