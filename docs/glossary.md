# Glossary

## Webhooks

**Delivery attempt**
: One HTTP request made for a webhook event. Retries are separate attempts with a new timestamp and signature.

**Endpoint**
: A consumer-owned URL registered to receive one FastID webhook event type.

**Event**
: A logical user-lifecycle occurrence emitted by FastID. One event can have multiple delivery attempts.

**Event ID**
: The stable UUID sent in `webhook-id` and in `event.event_id`. Consumers use it as the idempotency key.

**Idempotency key**
: A stable identifier atomically recorded by a consumer to prevent repeated side effects when an event is delivered
more than once.

**Raw body**
: The exact request bytes received before JSON parsing or re-serialization. These bytes are part of the signed content.

**Standard Webhooks headers**
: The `webhook-id`, `webhook-timestamp`, and `webhook-signature` headers used to identify and authenticate a delivery.

**Webhook secret**
: Endpoint-specific HMAC key material represented as `whsec_<base64>`. It must be stored and transmitted as a secret.

**Webhook signature**
: A versioned, base64-encoded HMAC-SHA256 authenticating
`webhook-id.webhook-timestamp.raw_body`. FastID currently emits version `v1`.
