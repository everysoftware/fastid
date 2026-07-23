# Glossary

## Webhooks

**Delivery attempt**
: One HTTP request made for a webhook event. Retries are separate attempts with a new timestamp and signature.

**Claim**
: An atomic operation that reserves a Webhook ID for processing. Only the request that creates the claim may apply the
event's side effects.

**Complete**
: Mark a claimed event as successfully processed so later deliveries are acknowledged without repeating work.

**Duplicate delivery**
: A delivery whose Webhook ID has already been claimed or completed. Consumers acknowledge it without applying the event
again.

**Endpoint**
: A consumer-owned URL registered to receive one FastID webhook event type.

**Event**
: A logical user-lifecycle occurrence emitted by FastID. One event can have multiple delivery attempts.

**Event ID**
: The logical domain event UUID sent in `event.event_id`. One event can create separate messages for multiple webhook
endpoints.

**Idempotency key**
: A stable identifier atomically recorded by a consumer to prevent repeated side effects when an event is delivered
more than once.

**Idempotency store**
: A component that atomically claims Webhook IDs and records their processing state. A production implementation must be
shared by all receiver processes and survive restarts.

**Webhook Endpoint**
: A configured webhook destination containing its URL, secret, event type, and activation state. FastID represents it
as `WebhookEndpoint`; a delivery refers to it through `endpoint_id`.

**Webhook ID**
: The delivery identifier sent in `webhook-id`. It is stable across retries of that delivery and is the consumer's
idempotency key. FastID stores it as `WebhookDelivery.id`.

**Release**
: Remove or expire an incomplete claim after processing fails, allowing a later FastID retry to claim the event again.

**Raw body**
: The exact request bytes received before JSON parsing or re-serialization. These bytes are part of the signed content.

**Standard Webhooks headers**
: The `webhook-id`, `webhook-timestamp`, and `webhook-signature` headers used to identify and authenticate a delivery.

**Webhook secret**
: Endpoint-specific HMAC key material represented as `whsec_<base64>`. It must be stored and transmitted as a secret.

**Webhook signature**
: A versioned, base64-encoded HMAC-SHA256 authenticating
`webhook-id.webhook-timestamp.raw_body`. FastID currently emits version `v1`.
