import base64
import binascii
import hashlib
import hmac
import logging
import os
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, ValidationError
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MAX_BODY_BYTES = 1024 * 1024
TIMESTAMP_TOLERANCE_SECONDS = 300
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///webhook-events.sqlite3"
EventProcessor = Callable[["WebhookEnvelope"], Awaitable[None]]

log = logging.getLogger(__name__)


class EventMetadata(PydanticBaseModel):
    event_id: UUID
    event_type: str = Field(min_length=1)
    timestamp: int


class WebhookEnvelope(PydanticBaseModel):
    event: EventMetadata
    data: dict[str, Any]


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class WebhookReceipt(Base):
    __tablename__ = "webhook_receipts"

    webhook_id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


def create_store_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class SQLAlchemyIdempotencyStore:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def claim(self, webhook_id: str) -> bool:
        try:
            async with self.session_factory() as session, session.begin():
                session.add(WebhookReceipt(webhook_id=webhook_id, status="processing"))
                await session.flush()
        except IntegrityError:
            return False
        return True

    async def complete(self, webhook_id: str) -> None:
        async with self.session_factory() as session, session.begin():
            await session.execute(
                update(WebhookReceipt)
                .where(WebhookReceipt.webhook_id == webhook_id)
                .values(status="completed", updated_at=utc_now())
            )

    async def release(self, webhook_id: str) -> None:
        async with self.session_factory() as session, session.begin():
            await session.execute(
                delete(WebhookReceipt).where(
                    WebhookReceipt.webhook_id == webhook_id,
                    WebhookReceipt.status == "processing",
                )
            )


def _secret_bytes(secret: str) -> bytes:
    if not secret.startswith("whsec_"):
        return secret.encode()
    try:
        return base64.b64decode(secret.removeprefix("whsec_"), validate=True)
    except (binascii.Error, ValueError) as exc:
        msg = "FASTID_WEBHOOK_SECRET contains invalid base64"
        raise ValueError(msg) from exc


def verify_signature(body: bytes, webhook_id: str, timestamp: int, signatures: str, secret: str) -> bool:
    signed = b".".join((webhook_id.encode(), str(timestamp).encode(), body))
    expected = base64.b64encode(hmac.new(_secret_bytes(secret), signed, hashlib.sha256).digest()).decode()
    return any(
        version == "v1" and hmac.compare_digest(value, expected)
        for signature in signatures.split()
        if "," in signature
        for version, value in (signature.split(",", 1),)
    )


def _required_header(request: Request, name: str) -> str:
    value = request.headers.get(name)
    if not value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Missing {name} header")
    return value


def _content_length(request: Request) -> int | None:
    value = request.headers.get("content-length")
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid Content-Length header") from exc


async def process_event(event: WebhookEnvelope) -> None:
    log.info(
        "Received FastID webhook: event_id=%s event_type=%s",
        event.event.event_id,
        event.event.event_type,
    )


async def _validated_event(request: Request) -> tuple[WebhookEnvelope, str]:
    declared_length = _content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Webhook body is too large")
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Webhook body is too large")

    webhook_id = _required_header(request, "webhook-id")
    timestamp_value = _required_header(request, "webhook-timestamp")
    signatures = _required_header(request, "webhook-signature")
    try:
        timestamp = int(timestamp_value)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook-timestamp header") from exc
    if abs(int(time.time()) - timestamp) > TIMESTAMP_TOLERANCE_SECONDS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Webhook timestamp is outside the allowed tolerance")
    if not verify_signature(body, webhook_id, timestamp, signatures, request.app.state.webhook_secret):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid webhook signature")

    try:
        event = WebhookEnvelope.model_validate_json(body)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook payload") from exc
    return event, webhook_id


async def _receive_webhook(request: Request, processor: EventProcessor) -> Response:
    event, webhook_id = await _validated_event(request)
    store: SQLAlchemyIdempotencyStore = request.app.state.idempotency_store
    try:
        claimed = await store.claim(webhook_id)
    except Exception as exc:
        log.exception("Could not claim FastID webhook: webhook_id=%s", webhook_id)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Webhook processing failed") from exc
    if not claimed:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    try:
        await processor(event)
        await store.complete(webhook_id)
    except Exception as exc:
        log.exception("FastID webhook processing failed: webhook_id=%s", webhook_id)
        try:
            await store.release(webhook_id)
        except Exception:
            log.exception("Could not release FastID webhook claim: webhook_id=%s", webhook_id)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Webhook processing failed") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def create_app(
    database_url: str | None = None,
    processor: EventProcessor = process_event,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        secret = os.getenv("FASTID_WEBHOOK_SECRET")
        if not secret:
            msg = "FASTID_WEBHOOK_SECRET is required"
            raise RuntimeError(msg)
        try:
            _secret_bytes(secret)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc

        selected_url = database_url or os.getenv("WEBHOOK_DATABASE_URL") or DEFAULT_DATABASE_URL
        engine = create_store_engine(selected_url)
        store = SQLAlchemyIdempotencyStore(async_sessionmaker(engine, expire_on_commit=False))
        await create_schema(engine)
        app.state.webhook_secret = secret
        app.state.idempotency_store = store
        try:
            yield
        finally:
            await engine.dispose()

    webhook_app = FastAPI(lifespan=lifespan)

    @webhook_app.post("/fastid-webhooks", status_code=status.HTTP_204_NO_CONTENT)
    async def receive_webhook(request: Request) -> Response:
        return await _receive_webhook(request, processor)

    return webhook_app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("examples.webhook_sqlalchemy:app", host="127.0.0.1", port=8000)
