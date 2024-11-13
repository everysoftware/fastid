from typing import Any, Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.authlib.dependencies import auth_backend
from app.authlib.schemas import BearerToken
from app.oauthlib.dependencies import OAuthName
from app.oauthlib.schemas import OAuthCallback
from app.obs.logger import logger_factory
from app.social.dependencies import SocialLoginDep

logger = logger_factory.create(__name__)
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
    callback: Annotated[OAuthCallback, Depends()],
) -> BearerToken:
    logger.info("OAuth callback received: request_url=%s", str(request.url))
    user = await service.authorize(oauth_name, callback)
    return auth_backend.create_bearer(user)


# @router.post(
#     "/telegram/token",
#     description="""
# Telegram does not support the classic OAuth2 Authorization Code flow.
# It passes user data to the redirect page in a fragment that is only accessible in the browser.""",
#     status_code=status.HTTP_200_OK,
# )
# async def telegram_token(
#     service: OAuthAccountsDep,
#     auth_data: TelegramCallback,
# ) -> BearerToken:
#     data = await service.sso_callback(OAuthProvider.telegram, auth_data)
#     return await service.sso_authorize(data)
#
#
# @router.get(
#     "/telegram/callback",
#     status_code=status.HTTP_200_OK,
# )
# async def telegram_callback(
#     service: UserServiceDep,
#     request: Request,
# ) -> Any:
#     bot_me = await service.bot.me()
#     return templates.TemplateResponse(
#         "telegram_login.html",
#         {
#             "request": request,
#             "bot_username": bot_me.username,
#             "redirect_uri": request.url_for("telegram_view_data"),
#         },
#     )
#
#
# @router.get(
#     "/telegram/view",
#     status_code=status.HTTP_200_OK,
# )
# def telegram_view_data(
#     auth_data: Annotated[TelegramCallback, Depends()],
# ) -> TelegramCallback:
#     return auth_data
#
#
# @router.post("/telegram/connect", status_code=status.HTTP_201_CREATED)
# async def telegram_connect(
#     service: UserServiceDep,
#     user: UserDep,
#     auth_data: TelegramCallback,
# ) -> OAuthAccountRead:
#     data = await service.sso_callback(OAuthProvider.telegram, auth_data)
#     return await service.sso_connect(user, data)
#
#
# @router.post(
#     "/{provider}/token",
#     description="Exchanges authorization code for token.",
#     status_code=status.HTTP_200_OK,
#     tags=["SSO"],
# )
# async def sso_token(
#     service: UserServiceDep,
#     provider: Annotated[OAuthProvider, Depends(valid_oauth)],
#     form: Annotated[SSOCallbackForm, Depends()],
# ) -> BearerToken:
#     callback = OAuthCallback(
#         code=form.code,
#         redirect_uri=form.redirect_uri,
#     )
#     data = await service.sso_callback(provider, callback)
#     return await service.sso_authorize(data)
#
