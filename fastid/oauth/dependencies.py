from typing import Annotated

from auth365.schemas import OAuth2Callback, TelegramCallback
from fastapi import Depends
from starlette.requests import Request

from fastid.core.dependencies import log
from fastid.database.utils import UUIDv7
from fastid.oauth.models import OAuthAccount
from fastid.oauth.use_cases import OAuthUseCases

OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]


async def get_account(service: OAuthAccountsDep, account_id: UUIDv7) -> OAuthAccount:
    return await service.get_one(account_id)


def valid_callback(oauth_name: str, request: Request) -> OAuth2Callback | TelegramCallback:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    callback: OAuth2Callback | TelegramCallback
    if oauth_name != "telegram":
        callback = OAuth2Callback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    return callback
