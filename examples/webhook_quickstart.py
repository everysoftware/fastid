import base64
import binascii
import hashlib
import hmac
import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status

log = logging.getLogger(__name__)


def _secret_bytes(secret: str) -> bytes:
    if not secret.startswith("whsec_"):
        return secret.encode()
    try:
        return base64.b64decode(secret.removeprefix("whsec_"), validate=True)
    except (binascii.Error, ValueError) as exc:
        msg = "FASTID_WEBHOOK_SECRET contains invalid base64"
        raise ValueError(msg) from exc


def verify_signature(body: bytes, webhook_id: str, timestamp: str, signatures: str, secret: str) -> bool:
    signed = b".".join((webhook_id.encode(), timestamp.encode(), body))
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


def _validate_payload(value: Any) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook payload")
    event = value.get("event")
    data = value.get("data")
    if not isinstance(event, dict) or not isinstance(data, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook payload")
    event_id = event.get("event_id")
    event_type = event.get("event_type")
    event_timestamp = event.get("timestamp")
    if not isinstance(event_id, str) or not isinstance(event_type, str) or not event_type.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook event")
    if type(event_timestamp) is not int:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook event")
    try:
        normalized_event_id = str(UUID(event_id))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid webhook event ID") from exc
    return normalized_event_id, event_type


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
    app.state.webhook_secret = secret
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/fastid-webhooks", status_code=status.HTTP_204_NO_CONTENT)
async def receive_webhook(request: Request) -> Response:
    body = await request.body()
    webhook_id = _required_header(request, "webhook-id")
    timestamp = _required_header(request, "webhook-timestamp")
    signatures = _required_header(request, "webhook-signature")
    if not verify_signature(body, webhook_id, timestamp, signatures, request.app.state.webhook_secret):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid webhook signature")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON body") from exc
    event_id, event_type = _validate_payload(payload)

    # Before production side effects, use an advanced receiver that checks freshness and claims webhook-id.
    log.info("Received FastID webhook: event_id=%s event_type=%s", event_id, event_type)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run("examples.webhook_quickstart:app", host="127.0.0.1", port=8000)
