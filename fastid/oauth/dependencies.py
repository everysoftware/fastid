from typing import Annotated

from fastapi import Depends
from fastlink.schemas import OAuth2Callback
from fastlink.telegram.schemas import TelegramCallback
from starlette.requests import Request

from fastid.core.dependencies import log
from fastid.oauth.use_cases import OAuthUseCases

OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]


def valid_callback(request: Request) -> OAuth2Callback:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    return OAuth2Callback.model_validate(request.query_params)


def valid_telegram_callback(request: Request) -> TelegramCallback:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    return TelegramCallback.model_validate(request.query_params)
