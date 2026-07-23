import asyncio
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from starlette import status

from examples.webhook_advanced import (
    MAX_BODY_BYTES,
    SQLAlchemyIdempotencyStore,
    WebhookEnvelope,
    create_app,
    create_schema,
    create_store_engine,
)
from tests.examples.webhook_helpers import SECRET, headers_for, payload, signed_request

CLAIM_COUNT = 10
EXPECTED_DUPLICATE_CLAIMS = CLAIM_COUNT - 1
EXPECTED_PROCESS_CALLS = 2


def database_url(tmp_path: Path) -> str:
    return f"sqlite+aiosqlite:///{tmp_path / 'webhooks.sqlite3'}"


def store_for(engine: AsyncEngine) -> SQLAlchemyIdempotencyStore:
    return SQLAlchemyIdempotencyStore(async_sessionmaker(engine, expire_on_commit=False))


async def test_claim_persists_across_store_instances(tmp_path: Path) -> None:
    url = database_url(tmp_path)
    first_engine = create_store_engine(url)
    second_engine = create_store_engine(url)
    first = store_for(first_engine)
    second = store_for(second_engine)
    await create_schema(first_engine)

    assert await first.claim("webhook-1")
    await first.complete("webhook-1")
    assert not await second.claim("webhook-1")

    await first_engine.dispose()
    await second_engine.dispose()


async def test_concurrent_claim_has_one_winner(tmp_path: Path) -> None:
    engine = create_store_engine(database_url(tmp_path))
    store = store_for(engine)
    await create_schema(engine)

    results = await asyncio.gather(*(store.claim("webhook-1") for _ in range(CLAIM_COUNT)))

    assert results.count(True) == 1
    assert results.count(False) == EXPECTED_DUPLICATE_CLAIMS
    await engine.dispose()


async def test_release_allows_retry(tmp_path: Path) -> None:
    engine = create_store_engine(database_url(tmp_path))
    store = store_for(engine)
    await create_schema(engine)
    assert await store.claim("webhook-1")

    await store.release("webhook-1")

    assert await store.claim("webhook-1")
    await engine.dispose()


def test_duplicate_is_acknowledged_once(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    processed: list[str] = []

    async def record(event: WebhookEnvelope) -> None:
        processed.append(str(event.event.event_id))

    value = payload()
    body, headers = signed_request(value)
    with TestClient(create_app(database_url(tmp_path), processor=record)) as client:
        first = client.post("/fastid-webhooks", content=body, headers=headers)
        duplicate = client.post("/fastid-webhooks", content=body, headers=headers)

    assert first.status_code == status.HTTP_204_NO_CONTENT
    assert duplicate.status_code == status.HTTP_204_NO_CONTENT
    assert processed == [value["event"]["event_id"]]
    assert headers["webhook-id"] != value["event"]["event_id"]


def test_processing_failure_releases_claim(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    calls = 0

    async def fail_once(event: WebhookEnvelope) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError(str(event.event.event_id))

    body, headers = signed_request(payload())
    with TestClient(create_app(database_url(tmp_path), processor=fail_once)) as client:
        failed = client.post("/fastid-webhooks", content=body, headers=headers)
        retried = client.post("/fastid-webhooks", content=body, headers=headers)

    assert failed.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert retried.status_code == status.HTTP_204_NO_CONTENT
    assert calls == EXPECTED_PROCESS_CALLS


def test_rejects_invalid_envelope(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = b"{}"
    headers = headers_for(body, "webhook-1")

    with TestClient(create_app(database_url(tmp_path))) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejects_invalid_signature(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, headers = signed_request(payload())
    headers["webhook-signature"] = "v1,invalid"

    with TestClient(create_app(database_url(tmp_path))) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_rejects_stale_timestamp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body, _ = signed_request(payload())
    headers = headers_for(body, "webhook-1", timestamp=int(time.time()) - 301)

    with TestClient(create_app(database_url(tmp_path))) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rejects_oversized_body(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FASTID_WEBHOOK_SECRET", SECRET)
    body = b"x" * (MAX_BODY_BYTES + 1)
    headers = headers_for(body, "webhook-1")

    with TestClient(create_app(database_url(tmp_path))) as client:
        response = client.post("/fastid-webhooks", content=body, headers=headers)

    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
