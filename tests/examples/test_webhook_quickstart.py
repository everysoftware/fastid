import pytest
from fastapi.testclient import TestClient
from starlette import status

from examples.webhook_quickstart import app
from tests.examples.webhook_helpers import SECRET, headers_for, payload, signed_request


def test_accepts_valid_webhook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_requires_secret_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FASTID_WEBHOOK_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="FASTID_WEBHOOK_SECRET is required"), TestClient(app):
        pass


def test_rejects_tampered_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body + b" ", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("header", ["webhook-id", "webhook-timestamp", "webhook-signature"])
def test_rejects_missing_header(monkeypatch: pytest.MonkeyPatch, header: str) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())
    headers.pop(header)

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_treats_webhook_id_and_timestamp_as_opaque_signature_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    value = payload()
    body, _ = signed_request(value)
    headers = headers_for(body, "opaque-webhook-id", timestamp="opaque-timestamp")

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert headers["webhook-id"] != value["event"]["event_id"]


def test_rejects_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = b"not-json"
    headers = headers_for(body, "event-1")

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejects_invalid_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = b"{}"
    headers = headers_for(body, "event-1")

    with TestClient(app) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
