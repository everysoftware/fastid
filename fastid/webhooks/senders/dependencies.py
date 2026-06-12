from typing import Annotated

import httpx
from fastapi import Depends

from fastid.webhooks.senders.httpx import WebhookSender

client = httpx.AsyncClient()


def get_sender() -> WebhookSender:
    return WebhookSender(client)


SenderDep = Annotated[WebhookSender, Depends(get_sender)]
