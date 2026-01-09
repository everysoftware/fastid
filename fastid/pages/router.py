from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastlink.schemas import JWKS, DiscoveryDocument

from fastid.auth.dependencies import cookie_transport
from fastid.auth.grants import AuthorizationCodeGrant
from fastid.auth.models import User
from fastid.auth.schemas import OAuth2ConsentRequest
from fastid.notify.schemas import UserAction
from fastid.oauth.dependencies import OAuthAccountsDep
from fastid.pages.dependencies import (
    get_user,
    get_user_or_none,
    is_action_verified,
    valid_consent,
)
from fastid.pages.openid import discovery_document, jwks
from fastid.pages.templating import templates

router = APIRouter()


@router.get("/")
def index() -> Response:
    return RedirectResponse(url="/login")


@router.get("/register")
def register(
    request: Request,
    user: Annotated[User | None, Depends(get_user_or_none)],
) -> Response:
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login")
def login(
    request: Request,
    user: Annotated[User | None, Depends(get_user_or_none)],
) -> Response:
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse("authorize.html", {"request": request})


@router.get("/authorize")
async def authorize(
    request: Request,
    user: Annotated[User | None, Depends(get_user_or_none)],
    consent: Annotated[OAuth2ConsentRequest, Depends(valid_consent)],
    authorization_code_grant: Annotated[AuthorizationCodeGrant, Depends()],
) -> Response:
    if user is None:
        assert consent.client_id is not None
        app = await authorization_code_grant.validate_client(consent.client_id)
        request.session["consent"] = consent.model_dump(mode="json")
        return templates.TemplateResponse("authorize.html", {"request": request, "app": app})
    # User is authenticated, redirect to specified redirect URI with code
    request.session.clear()
    redirect_uri = await authorization_code_grant.approve_consent(consent, user)
    return RedirectResponse(redirect_uri)


@router.get("/profile")
async def profile(
    request: Request,
    oauth_accounts: OAuthAccountsDep,
    user: Annotated[User, Depends(get_user)],
) -> Response:
    page = await oauth_accounts.paginate(user)
    connected = {a.provider for a in page.items}
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "connected_providers": connected},
    )


@router.get("/restore")
def restore_account(
    request: Request,
) -> Response:
    return templates.TemplateResponse(
        "restore-account.html",
        {"request": request},
    )


@router.get("/verify-action")
def verify_action(
    request: Request,
    verified: Annotated[bool, Depends(is_action_verified)],
    action: UserAction,
) -> Response:
    if verified:
        return RedirectResponse(f"/{action}")
    return templates.TemplateResponse(
        "verify-action.html",
        {"request": request},
    )


@router.get("/change-password")
def change_password(
    request: Request,
    user: Annotated[User | None, Depends(get_user_or_none)],
    verified: Annotated[bool, Depends(is_action_verified)],
) -> Response:
    if not verified:
        return RedirectResponse(f"/verify-action?action={UserAction.change_password}")
    return templates.TemplateResponse(
        "change-password.html",
        {"request": request, "user": user},
    )


@router.get("/change-email")
def change_email(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(is_action_verified)],
) -> Any:
    if not verified:
        return RedirectResponse(f"/verify-action?action={UserAction.change_email}")
    return templates.TemplateResponse(
        "change-email.html",
        {"request": request, "user": user},
    )


@router.get("/delete-account")
def delete_account(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(is_action_verified)],
) -> Response:
    if not verified:
        return RedirectResponse(f"/verify-action?action={UserAction.delete_account}")
    return templates.TemplateResponse(
        "delete-account.html",
        {"request": request, "user": user},
    )


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    response = RedirectResponse(url="/login")
    cookie_transport.delete_token(response)
    return response


@router.get("/.well-known/openid-configuration")
def openid_configuration() -> DiscoveryDocument:
    return discovery_document


@router.get("/.well-known/jwks.json")
def get_jwks() -> JWKS:
    return jwks
