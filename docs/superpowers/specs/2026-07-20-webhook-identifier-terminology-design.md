# Webhook Identifier Terminology Design

## Problem

FastID has three independent identifiers in its webhook flow:

- the configured destination currently represented by `Webhook.id`;
- the individual delivery represented by `WebhookDelivery.id`;
- the domain event represented by `event.event_id`.

Calling the configured destination simply a webhook makes `webhook_id` ambiguous. The Standard Webhooks
`webhook-id` header identifies the delivered webhook, not the configured destination or the domain event.

## Decision

FastID will use these domain terms:

- **Webhook Endpoint**: the configured URL, secret, event type, and activation state;
- **Webhook ID**: the stable identifier of one delivered webhook, sent in `webhook-id` and represented by
  `WebhookDelivery.id`;
- **Event ID**: the logical domain event identifier sent in `event.event_id`.

The Webhook ID remains stable across retries of the same delivery. One event can create multiple webhook deliveries,
each with its own Webhook ID, when it is sent to multiple endpoints.

## Code and persistence names

Domain terminology remains explicit in documentation and user-facing text. Attributes use the shortest unambiguous
name within their owning model:

| Concept | Code or persistence representation |
| --- | --- |
| Webhook Endpoint | `WebhookEndpoint` |
| Endpoint table | `webhook_endpoints` |
| Webhook Endpoint ID on a delivery | `WebhookDelivery.endpoint_id` |
| Endpoint relationship on a delivery | `WebhookDelivery.endpoint` |
| Webhook ID | `WebhookDelivery.id`, local variable `webhook_id`, HTTP header `webhook-id` |
| Event ID | `Event.event_id` and `WebhookDelivery.event_id` |

The former `Webhook` model, `webhooks` table, `WebhookDelivery.webhook_id` foreign key, and
`WebhookDelivery.webhook` relationship will be renamed accordingly. Public routes may remain under `/webhooks`
because that path names the webhook feature rather than one identifier.

## Signing and receiving

FastID signs `webhook_id.timestamp.raw_body`, where `webhook_id` is `WebhookDelivery.id`. Sender and receiver code
will consistently use the variable name `webhook_id`; it will not use `message_id` or `delivery_id` as aliases.

Receiver examples will treat `webhook-id` and `event.event_id` as independent values. The quick-start verifies only
the signature and treats the Webhook ID and timestamp as opaque signature inputs. Advanced examples additionally
validate timestamp freshness and use the Webhook ID as their idempotency key.

## Migration and compatibility

The database schema will rename `webhooks` to `webhook_endpoints` and the delivery foreign-key column to
`endpoint_id`, preserving existing identifiers and relationships. The external signing contract keeps the standard
header name `webhook-id`; only the value semantics are clarified as the Webhook ID represented by
`WebhookDelivery.id`.

Tests will verify that the header Webhook ID equals `WebhookDelivery.id`, differs independently from the Event ID,
and remains stable across retries.
