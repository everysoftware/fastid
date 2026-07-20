# ADR 0001: Use Only Standard Webhook Headers

- Status: Accepted
- Date: 2026-07-20

## Context

FastID sends both a legacy configurable `X-Webhook-*` signature protocol and the fixed Standard Webhooks protocol. The
protocols use different identifiers, signed representations, and signature encodings. Consumers therefore have two
ways to authenticate the same delivery, only one of which protects the exact transmitted bytes.

## Decision

FastID will send and support only `webhook-id`, `webhook-timestamp`, and `webhook-signature`. The signature will remain a
versioned base64 HMAC-SHA256 over `webhook-id.webhook-timestamp.raw_body`.

The legacy signing functions, verification function, configurable header names, and configurable signature algorithm
will be removed.

## Consequences

- New examples and integrations have one authentication contract.
- The stable event ID is unambiguously the idempotency key.
- Verification authenticates the exact transmitted body.
- Existing consumers of `X-Webhook-*` must migrate to Standard Webhooks headers.
- Supporting a future signing change will require a new version in `webhook-signature`, not a second header family.
