from typing import Any, Annotated

from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from starlette import status

from app.api.exceptions import ClientError
from app.auth.config import auth_settings
from app.auth.dependencies import UserManagerDep, UserDep
from app.authlib.dependencies import cookie_transport, auth_bus
from app.frontend.templating import templates
from app.notifylib.telegram import BotDep
from app.oauth.dependencies import OAuthAccountsDep, valid_callback
from app.oauth.providers import registry
from app.oauthlib.schemas import UniversalCallback

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get(
    "/login/{oauth_name}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_303_SEE_OTHER,
)
async def oauth_login(
    service: OAuthAccountsDep,
    oauth_name: str,
    redirect: bool = True,
) -> Any:
    url = await service.get_authorization_url(oauth_name)
    if not redirect:
        return url
    return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url=url)


@router.get(
    "/callback/{oauth_name}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    auth: UserManagerDep,
    oauth: OAuthAccountsDep,
    request: Request,
    oauth_name: str,
    callback: Annotated[UniversalCallback, Depends(valid_callback)],
) -> Any:
    at = auth_bus.parse_request(request, auto_error=False)
    response: Response = RedirectResponse(
        url=auth_settings.authorization_endpoint
    )
    if at is not None:
        try:
            user = await auth.get_userinfo(at)
        except ClientError:
            pass
        else:
            # Connect OAuth account to existing user
            await oauth.connect(user, oauth_name, callback)
            return response
    token = await oauth.authorize(oauth_name, callback)
    assert token.access_token is not None
    at = token.access_token
    return cookie_transport.set_token(response, at)


@router.get(
    "/revoke/{oauth_name}",
    status_code=status.HTTP_200_OK,
)
async def oauth_revoke(
    oauth: OAuthAccountsDep,
    user: UserDep,
    oauth_name: str,
) -> Any:
    await oauth.revoke(user, oauth_name)
    return RedirectResponse(url=auth_settings.authorization_endpoint)


@router.get(
    "/redirect/telegram",
    status_code=status.HTTP_200_OK,
)
async def telegram_redirect(request: Request, bot: BotDep) -> Any:
    return templates.TemplateResponse(
        request,
        "telegram-redirect.html",
        {
            "request": request,
            "redirect_uri": registry.inspect("telegram").redirect_uri,
            "bot_username": (await bot.me()).username,
        },
    )
