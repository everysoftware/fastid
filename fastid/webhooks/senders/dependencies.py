from typing import Annotated

import httpx
from fastapi import Depends

from fastid.webhooks.config import webhook_settings
from fastid.webhooks.senders.httpx import WebhookSender

timeout = httpx.Timeout(
    webhook_settings.read_timeout_seconds,
    connect=webhook_settings.connect_timeout_seconds,
    write=webhook_settings.write_timeout_seconds,
    pool=webhook_settings.pool_timeout_seconds,
)
limits = httpx.Limits(
    max_connections=webhook_settings.max_connections,
    max_keepalive_connections=webhook_settings.max_keepalive_connections,
)
client = httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=False, trust_env=False)


def get_sender() -> WebhookSender:
    return WebhookSender(client)


SenderDep = Annotated[WebhookSender, Depends(get_sender)]
