import asyncio
import logging
import secrets
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from prometheus_client import start_http_server
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import joinedload

from fastid.database.dependencies import get_uow_raw
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import naive_utc
from fastid.security.webhooks import generate_delivery_headers, get_timestamp, serialize_payload
from fastid.webhooks.config import webhook_settings
from fastid.webhooks.metrics import ATTEMPT_DURATION, ATTEMPTS, DISABLED_ENDPOINTS, DUE_DELIVERIES
from fastid.webhooks.models import WebhookAttempt, WebhookDelivery, WebhookDeliveryStatus, WebhookEndpoint
from fastid.webhooks.senders.dependencies import client
from fastid.webhooks.senders.httpx import WebhookResponse, WebhookSender

log = logging.getLogger(__name__)
HTTP_OK = 200
HTTP_MULTIPLE_CHOICES = 300
HTTP_GONE = 410
RANDOM = secrets.SystemRandom()


def get_retry_delay(attempt_number: int, retry_after_seconds: int | None, *, jitter: float | None = None) -> int:
    delay = webhook_settings.retry_delays_seconds[attempt_number]
    if jitter is None:
        jitter = RANDOM.uniform(1 - webhook_settings.retry_jitter_ratio, 1 + webhook_settings.retry_jitter_ratio)
    delay = max(0, int(delay * jitter))
    if retry_after_seconds is not None:
        retry_after = min(retry_after_seconds, webhook_settings.retry_after_max_seconds)
        delay = max(delay, retry_after)
    return delay


@dataclass(frozen=True)
class ClaimedDelivery:
    webhook_id: UUID
    event_id: UUID
    event_type: str
    payload: dict[str, object]
    endpoint_url: str
    endpoint_secret: str


class WebhookWorker:
    def __init__(self, sender: WebhookSender | None = None) -> None:
        self.sender = sender or WebhookSender(client)
        self.stopping = asyncio.Event()
        self.semaphore = asyncio.Semaphore(webhook_settings.worker_concurrency)

    async def run(self) -> None:
        log.info("Webhook worker started")
        while not self.stopping.is_set():
            count = await self.run_once()
            if count == 0:
                with suppress(TimeoutError):
                    await asyncio.wait_for(self.stopping.wait(), timeout=webhook_settings.worker_poll_seconds)
        log.info("Webhook worker stopped")

    async def run_once(self) -> int:
        deliveries = await self._claim()
        await asyncio.gather(*(self._process_with_limit(delivery) for delivery in deliveries))
        return len(deliveries)

    async def _claim(self) -> list[ClaimedDelivery]:
        now = naive_utc()
        lease = now + timedelta(seconds=webhook_settings.worker_lease_seconds)
        uow = get_uow_raw()
        async with uow:
            stmt = (
                select(WebhookDelivery)
                .options(joinedload(WebhookDelivery.endpoint))
                .where(
                    WebhookDelivery.next_attempt_at <= now,
                    or_(
                        WebhookDelivery.status == WebhookDeliveryStatus.pending,
                        (WebhookDelivery.status == WebhookDeliveryStatus.processing)
                        & (WebhookDelivery.leased_until <= now),
                    ),
                )
                .order_by(WebhookDelivery.next_attempt_at, WebhookDelivery.created_at)
                .limit(webhook_settings.worker_batch_size)
                .with_for_update(skip_locked=True, of=WebhookDelivery)
            )
            rows = list((await uow.session.scalars(stmt)).all())
            due_count = await uow.session.scalar(
                select(func.count())
                .select_from(WebhookDelivery)
                .where(
                    WebhookDelivery.next_attempt_at <= now,
                    or_(
                        WebhookDelivery.status == WebhookDeliveryStatus.pending,
                        (WebhookDelivery.status == WebhookDeliveryStatus.processing)
                        & (WebhookDelivery.leased_until <= now),
                    ),
                )
            )
            DUE_DELIVERIES.set(due_count or 0)
            claimed: list[ClaimedDelivery] = []
            for delivery in rows:
                if not delivery.endpoint.is_active:
                    delivery.status = WebhookDeliveryStatus.cancelled
                    delivery.completed_at = now
                    delivery.error = "endpoint disabled"
                    continue
                delivery.status = WebhookDeliveryStatus.processing
                delivery.leased_until = lease
                claimed.append(
                    ClaimedDelivery(
                        webhook_id=delivery.id,
                        event_id=delivery.event_id,
                        event_type=str(delivery.event_type),
                        payload=delivery.payload,
                        endpoint_url=delivery.endpoint.url,
                        endpoint_secret=delivery.endpoint.secret,
                    )
                )
            return claimed
        return []  # pragma: no cover - the unit of work context always enters

    async def _process_with_limit(self, delivery: ClaimedDelivery) -> None:
        async with self.semaphore:
            await self._process(delivery)

    async def _process(self, delivery: ClaimedDelivery) -> None:
        timestamp = get_timestamp()
        body = serialize_payload(delivery.payload)
        headers = generate_delivery_headers(
            body,
            str(delivery.webhook_id),
            timestamp,
            delivery.endpoint_secret,
        )
        response = await self.sender.send(delivery.endpoint_url, body, headers)
        await self._record(delivery.webhook_id, delivery.event_type, timestamp, headers, response)

    async def _record(
        self,
        webhook_id: UUID,
        event_type: str,
        timestamp: int,
        headers: dict[str, str],
        response: WebhookResponse,
    ) -> None:
        now = naive_utc()
        uow = get_uow_raw()
        async with uow:
            delivery = await uow.webhook_deliveries.get(webhook_id)
            endpoint = await uow.webhook_endpoints.get(delivery.endpoint_id)
            attempt_number = delivery.attempt_count + 1
            stored_headers = {
                key: "[redacted]" if "signature" in key.lower() else value for key, value in headers.items()
            }
            request = {"headers": stored_headers, "body": delivery.payload}
            attempt = WebhookAttempt(
                delivery_id=delivery.id,
                attempt_number=attempt_number,
                timestamp=timestamp,
                request=request,
                status_code=response.status_code,
                response=response.content,
                error=response.error,
                duration_ms=response.duration_ms,
            )
            await uow.webhook_attempts.add(attempt)
            delivery.attempt_count = attempt_number
            delivery.request = request
            delivery.status_code = response.status_code
            delivery.response = response.content
            delivery.error = response.error
            delivery.leased_until = None

            if HTTP_OK <= response.status_code < HTTP_MULTIPLE_CHOICES:
                delivery.status = WebhookDeliveryStatus.succeeded
                delivery.completed_at = now
                outcome = "succeeded"
            elif response.status_code == HTTP_GONE:
                await self._disable(uow, endpoint, delivery, now, "endpoint returned 410 Gone")
                outcome = "gone"
                DISABLED_ENDPOINTS.labels(reason="gone").inc()
            elif attempt_number >= len(webhook_settings.retry_delays_seconds):
                await self._disable(uow, endpoint, delivery, now, "delivery retries exhausted")
                outcome = "exhausted"
                DISABLED_ENDPOINTS.labels(reason="exhausted").inc()
            else:
                delay = get_retry_delay(attempt_number, response.retry_after_seconds)
                delivery.status = WebhookDeliveryStatus.pending
                delivery.next_attempt_at = now + timedelta(seconds=delay)
                outcome = "retry"
            ATTEMPTS.labels(event_type=event_type, outcome=outcome).inc()
            ATTEMPT_DURATION.labels(event_type=event_type).observe(response.duration_ms / 1000)
            log.info(
                "Webhook attempt completed: webhook_id=%s event_id=%s attempt=%d status_code=%d state=%s duration_ms=%d",
                delivery.id,
                delivery.event_id,
                attempt_number,
                response.status_code,
                delivery.status,
                response.duration_ms,
            )

    @staticmethod
    async def _disable(
        uow: SQLAlchemyUOW, endpoint: WebhookEndpoint, delivery: WebhookDelivery, now: datetime, reason: str
    ) -> None:
        delivery.status = (
            WebhookDeliveryStatus.exhausted if delivery.status_code != HTTP_GONE else WebhookDeliveryStatus.cancelled
        )
        delivery.completed_at = now
        endpoint.is_active = False
        endpoint.disabled_at = now
        endpoint.disabled_reason = reason
        await uow.session.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.endpoint_id == endpoint.id,
                WebhookDelivery.id != delivery.id,
                WebhookDelivery.status.in_((WebhookDeliveryStatus.pending, WebhookDeliveryStatus.processing)),
            )
            .values(status=WebhookDeliveryStatus.cancelled, completed_at=now, error="endpoint disabled")
        )


async def run_worker() -> None:
    if webhook_settings.worker_metrics_port > 0:
        start_http_server(webhook_settings.worker_metrics_port)
    worker = WebhookWorker()
    try:
        await worker.run()
    finally:
        await client.aclose()


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(run_worker())


if __name__ == "__main__":
    main()
