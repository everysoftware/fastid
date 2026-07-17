import pytest

from fastid.security.webhooks import (
    generate_delivery_headers,
    generate_headers,
    generate_secret,
    serialize_payload,
    verify_headers,
    verify_standard_headers,
)
from tests.mocks import WEBHOOK_ID, WEBHOOK_PAYLOAD, WEBHOOK_TEST_DATA, WEBHOOK_TIMESTAMP


@pytest.mark.parametrize(
    ("timestamp", "webhook_id", "generate_secret_key", "verify_secret_key", "expected"), WEBHOOK_TEST_DATA
)
def test_verify_headers(
    timestamp: int, webhook_id: str, generate_secret_key: str, verify_secret_key: str, *, expected: bool
) -> None:
    headers = generate_headers(WEBHOOK_PAYLOAD, timestamp, webhook_id, generate_secret_key)
    assert verify_headers(WEBHOOK_PAYLOAD, headers, verify_secret_key) == expected


@pytest.mark.parametrize("secret", ["legacy-secret", generate_secret()])
def test_verify_standard_headers(secret: str) -> None:
    body = serialize_payload(WEBHOOK_PAYLOAD)
    headers = generate_delivery_headers(WEBHOOK_PAYLOAD, body, WEBHOOK_ID, "delivery-id", WEBHOOK_TIMESTAMP, secret)

    assert verify_standard_headers(body, headers, secret)
    assert not verify_standard_headers(body + b" ", headers, secret)
    assert not verify_standard_headers(body, headers, "wrong-secret")


def test_standard_signature_uses_exact_utf8_body() -> None:
    payload = {"message": "Привет"}
    body = serialize_payload(payload)
    headers = generate_delivery_headers(payload, body, WEBHOOK_ID, "delivery-id", WEBHOOK_TIMESTAMP, "secret")

    assert b"\\u" not in body
    assert verify_standard_headers(body, {key.upper(): value for key, value in headers.items()}, "secret")
