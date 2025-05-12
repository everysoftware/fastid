from typing import Annotated

from fastapi import Depends
from fastlink.schemas import OAuth2Callback
from fastlink.telegram.schemas import TelegramCallback
from starlette.requests import Request

from fastid.core.dependencies import log
from fastid.database.utils import UUIDv7
from fastid.oauth.models import OAuthAccount
from fastid.oauth.use_cases import OAuthUseCases

OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]


async def get_account(service: OAuthAccountsDep, account_id: UUIDv7) -> OAuthAccount:
    return await service.get_one(account_id)


def valid_callback(provider: str, request: Request) -> OAuth2Callback | TelegramCallback:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    callback: OAuth2Callback | TelegramCallback
    if provider != "telegram":
        callback = OAuth2Callback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    return callback
