from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from fastlink import TelegramSSO
from fastlink.schemas import OAuth2Callback
from fastlink.telegram.schemas import TelegramCallback
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from fastid.auth.config import auth_settings
from fastid.auth.dependencies import UserDep, UserOrNoneDep, cookie_transport
from fastid.core.dependencies import log
from fastid.database.schemas import PageDTO
from fastid.oauth.clients.dependencies import get_telegram_sso
from fastid.oauth.dependencies import OAuthAccountsDep
from fastid.oauth.schemas import InspectProviderResponse, OAuthAccountDTO

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
    return await service.inspect(provider)


@router.get(
    "/login/{provider}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def oauth_login(
    service: OAuthAccountsDep,
    provider: str,
) -> Any:
    url = await service.get_login_url(provider)
    return RedirectResponse(status_code=status.HTTP_307_TEMPORARY_REDIRECT, url=url)


@router.get(
    "/callback/telegram",
    status_code=status.HTTP_200_OK,
)
async def telegram_callback(
    service: OAuthAccountsDep,
    request: Request,
    user: UserOrNoneDep,
    callback: Annotated[TelegramCallback, Depends()],
) -> Any:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    response: Response = RedirectResponse(url=auth_settings.authorization_endpoint)
    if user is not None:
        await service.connect(user, "telegram", callback)
        return response
    token_response = await service.login("telegram", callback)
    at = token_response.access_token
    assert at is not None
    return cookie_transport.set_token(response, at)


@router.get(
    "/callback/{provider}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    service: OAuthAccountsDep,
    request: Request,
    user: UserOrNoneDep,
    provider: str,
    callback: Annotated[OAuth2Callback, Depends()],
) -> Any:
    log.info("OAuth callback received: request_url=%s", str(request.url))
    response: Response = RedirectResponse(url=auth_settings.authorization_endpoint)
    if user is not None:
        await service.connect(user, provider, callback)
        return response
    token_response = await service.login(provider, callback)
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
async def telegram_redirect(sso: Annotated[TelegramSSO, Depends(get_telegram_sso)]) -> Any:
    async with sso:
        content = await sso.widget()
        return HTMLResponse(content=content)


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
