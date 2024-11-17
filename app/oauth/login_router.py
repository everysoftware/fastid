from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from starlette import status

from app.authlib.dependencies import cookie_transport
from app.frontend.templating import templates
from app.main import logging
from app.oauth.dependencies import SocialLoginDep
from app.oauthlib.dependencies import OAuthName
from app.oauthlib.schemas import OAuthCallback, TelegramCallback

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
) -> Any:
    logger.info("OAuth callback received: request_url=%s", str(request.url))
    callback: Any
    if oauth_name != OAuthName.telegram:
        callback = OAuthCallback.model_validate(request.query_params)
    else:
        callback = TelegramCallback.model_validate(request.query_params)
    token = await service.authorize(oauth_name, callback)
    response: Response = RedirectResponse(url="/authorize")
    assert token.access_token is not None
    response = cookie_transport.set_token(response, token.access_token)
    return response


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
