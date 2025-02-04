from typing import Annotated

from auth365.schemas import OAuth2Callback, TelegramCallback
from fastapi import Depends
from starlette.requests import Request

from app.base.types import UUID
from app.logging.dependencies import log
from app.oauth.models import OAuthAccount
from app.oauth.service import OAuthUseCases

OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]


async def get_account(service: OAuthAccountsDep, account_id: UUID) -> OAuthAccount:
    return await service.get_one(account_id)


def valid_callback(oauth_name: str, request: Request) -> OAuth2Callback | TelegramCallback:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    callback: OAuth2Callback | TelegramCallback
    if oauth_name != "telegram":
        callback = OAuth2Callback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    return callback
