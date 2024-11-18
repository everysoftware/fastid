from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from app.authlib.oauth import OAuth2Callback
from app.base.types import UUID
from app.main import logging
from app.oauth.models import OAuthAccount
from app.oauth.schemas import OAuthName
from app.oauth.service import OAuthUseCases
from app.oauthlib.schemas import TelegramCallback, UniversalCallback

logger = logging.get_logger(__name__)
OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]


async def get_account(
    service: OAuthAccountsDep, account_id: UUID
) -> OAuthAccount:
    return await service.get_one(account_id)


def valid_callback(
    oauth_name: OAuthName, request: Request
) -> UniversalCallback:
    logger.info("OAuth callback received: request_url=%s", str(request.url))
    callback: UniversalCallback
    if oauth_name != OAuthName.telegram:
        callback = OAuth2Callback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    return callback
