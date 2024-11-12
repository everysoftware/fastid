from typing import Any

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.oauthlib.dependencies import OAuthName
from app.social_login.dependencies import SocialLoginDep

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get(
    "/login/{provider}",
    description="Redirects user to the provider's login page.",
    status_code=status.HTTP_303_SEE_OTHER,
)
async def oauth_login(
    service: SocialLoginDep,
    oauth_name: OAuthName,
) -> Any:
    url = await service.login(oauth_name)
    response = RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url=url)
    return response


@router.get(
    "/callback/{provider}",
    status_code=status.HTTP_200_OK,
)
async def oauth_callback(
    provider: OAuthName,
    request: Request,
    code: str,
    state: str,
    scope: str | None = None,
) -> dict[str, Any]:
    return {
        "url": str(request.url),
        "provider": provider,
        "code": code,
        "scope": scope,
        "state": state,
    }


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
