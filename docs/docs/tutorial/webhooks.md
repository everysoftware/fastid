# Webhooks

FastID sends user lifecycle events to every active endpoint subscribed to the event type. Delivery is asynchronous,
durable, and at least once: consumers must treat `webhook-id` as an idempotency key because a request can be repeated
after a timeout or worker crash. Delivery order is not guaranteed.

## Request format

Each request is a JSON `POST`. The existing `X-Webhook-*` headers remain available, and new integrations should verify
the Standard Webhooks headers:

- `webhook-id`: logical event UUID, unchanged for retries.
- `webhook-timestamp`: Unix timestamp for the delivery attempt.
- `webhook-signature`: `v1,<base64 HMAC-SHA256>` signature.

The signed value is the exact byte sequence `webhook-id.webhook-timestamp.raw_body`. Verify the raw request body before
parsing JSON; parsing and serializing it again can change the bytes.

```python
from fastapi import FastAPI, Header, Request

from fastid.security.webhooks import verify_standard_headers

app = FastAPI()


@app.post("/fastid-webhooks")
async def receive(request: Request) -> dict[str, bool]:
    body = await request.body()
    if not verify_standard_headers(body, request.headers, "whsec_..."):
        return {"accepted": False}
    event = await request.json()
    # Atomically record event["event"]["event_id"] before applying side effects.
    return {"accepted": True}
```

The payload remains backward compatible:

```json
{
  "event": {
    "event_type": "user_registration",
    "event_id": "019b...",
    "timestamp": 1784293200
  },
  "data": {
    "user": {
      "id": "019b...",
      "email": "person@example.com"
    }
  }
}
```

User events that historically exposed user fields directly in `data` continue to include those fields during the
compatibility period; use `data.user` in new consumers.

## Delivery behavior

A `2xx` response completes delivery. Other responses and network failures are retried with jittered exponential
backoff for roughly three days. FastID respects `Retry-After` up to 24 hours, never follows redirects, disables an
endpoint immediately after `410 Gone`, and disables it after all attempts are exhausted.

The API transaction stores delivery records; a separate worker sends them:

```console
python -m fastid.webhooks.worker
```

Docker Compose starts this worker automatically. Its Prometheus metrics are exposed on port `9101` inside the Compose
network. Delivery and attempt history is also visible in the FastID admin application.

## Endpoint security

Production endpoints must use HTTPS, contain no URL credentials, and resolve only to public IP addresses. FastID pins
the validated address for the connection and does not follow redirects. Keep the worker in an egress-restricted network
as defense in depth. Local HTTP and private-address endpoints require the explicit
`FASTID_WEBHOOK_ALLOW_INSECURE_URLS=true` development setting.
