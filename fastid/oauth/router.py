from typing import Annotated, Any

from auth365.schemas import OAuth2Callback, TelegramCallback
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from starlette import status

from fastid.auth.config import auth_settings
from fastid.auth.dependencies import UserDep, cookie_transport, get_optional_user
from fastid.auth.models import User
from fastid.database.schemas import PageDTO
from fastid.oauth.config import oauth_settings
from fastid.oauth.dependencies import OAuthAccountsDep, valid_callback
from fastid.oauth.schemas import OAuthAccountDTO
from fastid.pages.templating import templates

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get(
    "/login/{oauth_name}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def oauth_login(
    service: OAuthAccountsDep,
    oauth_name: str,
    *,
    redirect: bool = True,
) -> Any:
    url = await service.get_authorization_url(oauth_name)
    if not redirect:
        return url
    return RedirectResponse(status_code=status.HTTP_307_TEMPORARY_REDIRECT, url=url)


@router.get(
    "/callback/{oauth_name}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    oauth: OAuthAccountsDep,
    user: Annotated[User | None, Depends(get_optional_user)],
    oauth_name: str,
    callback: Annotated[OAuth2Callback | TelegramCallback, Depends(valid_callback)],
) -> Any:
    response: Response = RedirectResponse(url=auth_settings.authorization_endpoint)
    if user is not None:
        await oauth.connect(user, oauth_name, callback)
        return response
    token_response = await oauth.authorize(oauth_name, callback)
    at = token_response.access_token
    assert at is not None
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
async def telegram_redirect(
    request: Request,
) -> Any:
    return templates.TemplateResponse(
        request,
        "telegram-redirect.html",
        {
            "request": request,
            "redirect_uri": f"{oauth_settings.base_redirect_url}/telegram",
        },
    )


@router.get(
    "/",
    response_model=PageDTO[OAuthAccountDTO],
    status_code=status.HTTP_200_OK,
)
async def paginate(
    service: OAuthAccountsDep,
    user: UserDep,
) -> Any:
    return await service.paginate(user)
