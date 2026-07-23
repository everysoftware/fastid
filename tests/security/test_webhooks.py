import pytest

from fastid.security.webhooks import (
    generate_delivery_headers,
    generate_secret,
    serialize_payload,
    verify_standard_headers,
)
from tests.mocks import WEBHOOK_ID, WEBHOOK_PAYLOAD, WEBHOOK_TIMESTAMP


@pytest.mark.parametrize("secret", ["plain-secret", generate_secret()])
def test_verify_standard_headers(secret: str) -> None:
    body = serialize_payload(WEBHOOK_PAYLOAD)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, secret)

    assert set(headers) == {
        "webhook-id",
        "webhook-timestamp",
        "webhook-signature",
        "Content-Type",
        "User-Agent",
    }
    assert verify_standard_headers(body, headers, secret)
    assert not verify_standard_headers(body + b" ", headers, secret)
    assert not verify_standard_headers(body, headers, "wrong-secret")


def test_standard_signature_uses_exact_utf8_body() -> None:
    payload = {"message": "Привет"}
    body = serialize_payload(payload)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, "secret")

    assert b"\\u" not in body
    assert verify_standard_headers(body, {key.upper(): value for key, value in headers.items()}, "secret")


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"webhook-id": WEBHOOK_ID, "webhook-timestamp": "invalid", "webhook-signature": "v1,value"},
        {"webhook-id": "", "webhook-timestamp": str(WEBHOOK_TIMESTAMP), "webhook-signature": "v1,value"},
        {"webhook-id": WEBHOOK_ID, "webhook-timestamp": str(WEBHOOK_TIMESTAMP), "webhook-signature": ""},
    ],
)
def test_verify_standard_headers_rejects_malformed_headers(headers: dict[str, str]) -> None:
    assert not verify_standard_headers(b"{}", headers, "secret")


def test_verify_standard_headers_rejects_stale_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    body = serialize_payload(WEBHOOK_PAYLOAD)
    headers = generate_delivery_headers(body, WEBHOOK_ID, WEBHOOK_TIMESTAMP, "secret")
    monkeypatch.setattr("fastid.security.webhooks.time.time", lambda: WEBHOOK_TIMESTAMP + 301)

    assert not verify_standard_headers(body, headers, "secret")


def test_invalid_prefixed_secret_is_a_configuration_error() -> None:
    with pytest.raises(ValueError, match="Invalid whsec_ webhook secret"):
        generate_delivery_headers(b"{}", WEBHOOK_ID, WEBHOOK_TIMESTAMP, "whsec_not-base64")
