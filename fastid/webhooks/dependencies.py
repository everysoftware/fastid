from typing import Annotated

from fastapi import Depends

from fastid.webhooks.use_cases import WebhookUseCases

WebhooksDep = Annotated[WebhookUseCases, Depends()]
