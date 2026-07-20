import asyncio

import pytest
from fastapi.testclient import TestClient
from starlette import status

from examples.webhook_advanced import (
    MAX_BODY_BYTES,
    InMemoryIdempotencyStore,
    WebhookEnvelope,
    create_app,
)
from tests.examples.webhook_helpers import SECRET, headers_for, payload, signed_request

CLAIM_COUNT = 20
EXPECTED_DUPLICATE_CLAIMS = CLAIM_COUNT - 1
EXPECTED_PROCESS_CALLS = 2


async def test_concurrent_claim_has_one_winner() -> None:
    store = InMemoryIdempotencyStore()

    results = await asyncio.gather(*(store.claim("event-1") for _ in range(CLAIM_COUNT)))

    assert results.count(True) == 1
    assert results.count(False) == EXPECTED_DUPLICATE_CLAIMS


async def test_release_allows_retry() -> None:
    store = InMemoryIdempotencyStore()
    assert await store.claim("event-1")

    await store.release("event-1")

    assert await store.claim("event-1")


def test_duplicate_is_acknowledged_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    processed: list[str] = []

    async def record(event: WebhookEnvelope) -> None:
        processed.append(str(event.event.event_id))

    body, headers = signed_request(payload())
    with TestClient(create_app(processor=record)) as client:
        first = client.post("/fastid-webhooks", content=body, headers=headers)
        duplicate = client.post("/fastid-webhooks", content=body, headers=headers)

    assert first.status_code == status.HTTP_204_NO_CONTENT
    assert duplicate.status_code == status.HTTP_204_NO_CONTENT
    assert processed == [headers["webhook-id"]]


def test_rejects_declared_oversized_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())
    headers["content-length"] = str(MAX_BODY_BYTES + 1)

    with TestClient(create_app()) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


def test_rejects_actual_oversized_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = b"x" * (MAX_BODY_BYTES + 1)
    headers = headers_for(body, "event-1")

    with TestClient(create_app()) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


def test_rejects_invalid_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    value = payload()
    value["event"]["event_type"] = ""
    body, headers = signed_request(value)

    with TestClient(create_app()) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejects_header_payload_id_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    value = payload()
    body, _ = signed_request(value)
    headers = headers_for(body, "00000000-0000-0000-0000-000000000000")

    with TestClient(create_app()) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_processing_failure_releases_claim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    calls = 0

    async def fail_once(event: WebhookEnvelope) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError(str(event.event.event_id))

    body, headers = signed_request(payload())
    with TestClient(create_app(processor=fail_once)) as client:
        failed = client.post("/fastid-webhooks", content=body, headers=headers)
        retried = client.post("/fastid-webhooks", content=body, headers=headers)

    assert failed.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert retried.status_code == status.HTTP_204_NO_CONTENT
    assert calls == EXPECTED_PROCESS_CALLS
