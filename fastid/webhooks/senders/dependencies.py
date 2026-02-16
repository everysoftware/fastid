from typing import Annotated

import httpx
from fastapi import Depends

from fastid.webhooks.senders.httpx import WebhookSender


def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


def get_sender(client: Annotated[httpx.AsyncClient, Depends(get_client)]) -> WebhookSender:
    return WebhookSender(client)


SenderDep = Annotated[WebhookSender, Depends(get_sender)]
