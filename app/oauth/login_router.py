from typing import Any

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.authlib.schemas import TokenResponse
from app.main import logging
from app.oauth.dependencies import SocialLoginDep
from app.oauthlib.dependencies import OAuthName
from app.oauthlib.schemas import OAuthCallback, TelegramCallback
from app.frontend.templating import templates

logger = logging.get_logger(__name__)
router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get(
    "/login/{oauth_name}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_303_SEE_OTHER,
)
async def oauth_login(
    service: SocialLoginDep, oauth_name: OAuthName, redirect: bool = True
) -> Any:
    url = await service.login(oauth_name)
    if not redirect:
        return url
    return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url=url)


@router.get(
    "/callback/{oauth_name}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    service: SocialLoginDep,
    oauth_name: OAuthName,
    request: Request,
) -> TokenResponse:
    logger.info("OAuth callback received: request_url=%s", str(request.url))
    callback: Any
    if oauth_name != OAuthName.telegram:
        callback = OAuthCallback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    return await service.authorize(oauth_name, callback)


@router.get(
    "/redirect/telegram",
    status_code=status.HTTP_200_OK,
)
def telegram_redirect(
    request: Request,
) -> Any:
    return templates.TemplateResponse(
        request,
        "telegram_redirect.html",
        {
            "redirect_uri": request.url_for(
                "oauth_callback", oauth_name="telegram"
            )
        },
    )
