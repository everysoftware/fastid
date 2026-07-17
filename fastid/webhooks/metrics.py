from prometheus_client import Counter, Gauge, Histogram

ATTEMPTS = Counter(
    "fastid_webhook_attempts_total",
    "Webhook delivery attempts by event type and outcome.",
    ["event_type", "outcome"],
)
ATTEMPT_DURATION = Histogram(
    "fastid_webhook_attempt_duration_seconds",
    "Webhook delivery attempt duration.",
    ["event_type"],
)
DUE_DELIVERIES = Gauge(
    "fastid_webhook_due_deliveries",
    "Webhook deliveries currently due for processing.",
)
DISABLED_ENDPOINTS = Counter(
    "fastid_webhook_disabled_endpoints_total",
    "Webhook endpoints disabled by reason.",
    ["reason"],
)
