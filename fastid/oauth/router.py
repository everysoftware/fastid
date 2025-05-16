from typing import Annotated, Any

from aiogram import Bot
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastlink.schemas import OAuth2Callback
from fastlink.telegram.schemas import TelegramCallback
from starlette import status

from fastid.auth.config import auth_settings
from fastid.auth.dependencies import UserDep, cookie_transport, get_optional_user
from fastid.auth.models import User
from fastid.database.schemas import PageDTO
from fastid.notify.clients.dependencies import get_bot
from fastid.oauth.config import oauth_settings
from fastid.oauth.dependencies import OAuthAccountsDep, valid_callback
from fastid.oauth.schemas import InspectProviderResponse, OAuthAccountDTO
from fastid.pages.templating import templates

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get(
    "/inspect/{provider}",
    description="Inspect the provider",
    response_model=InspectProviderResponse,
    status_code=status.HTTP_200_OK,
)
async def oauth_inspect(
    service: OAuthAccountsDep,
    provider: str,
) -> Any:
    login_url = await service.get_authorization_url(provider)
    return InspectProviderResponse(login_url=login_url)


@router.get(
    "/login/{provider}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def oauth_login(
    service: OAuthAccountsDep,
    provider: str,
) -> Any:
    url = await service.get_authorization_url(provider)
    return RedirectResponse(status_code=status.HTTP_307_TEMPORARY_REDIRECT, url=url)


@router.get(
    "/callback/{provider}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    service: OAuthAccountsDep,
    user: Annotated[User | None, Depends(get_optional_user)],
    provider: str,
    callback: Annotated[OAuth2Callback | TelegramCallback, Depends(valid_callback)],
) -> Any:
    response: Response = RedirectResponse(url=auth_settings.authorization_endpoint)
    if user is not None:
        await service.connect(user, provider, callback)
        return response
    token_response = await service.authorize(provider, callback)
    at = token_response.access_token
    assert at is not None
    return cookie_transport.set_token(response, at)


@router.get(
    "/revoke/{provider}",
    status_code=status.HTTP_200_OK,
)
async def oauth_revoke(
    service: OAuthAccountsDep,
    user: UserDep,
    provider: str,
) -> Any:
    await service.revoke(user, provider)
    return RedirectResponse(url=auth_settings.authorization_endpoint)


@router.get(
    "/redirect/telegram",
    status_code=status.HTTP_200_OK,
)
async def telegram_redirect(request: Request, bot: Annotated[Bot, Depends(get_bot)]) -> Any:
    async with bot:
        me = await bot.get_me()
        return templates.TemplateResponse(
            request,
            "telegram-redirect.html",
            {
                "request": request,
                "redirect_uri": f"{oauth_settings.base_redirect_url}/telegram",
                "bot_username": me.username,
            },
        )


@router.get(
    "/accounts",
    response_model=PageDTO[OAuthAccountDTO],
    status_code=status.HTTP_200_OK,
)
async def paginate(
    service: OAuthAccountsDep,
    user: UserDep,
) -> Any:
    return await service.paginate(user)
