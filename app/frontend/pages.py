from typing import Annotated, Any, Literal

from auth365.schemas import JWKS, DiscoveryDocument
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse

from app.auth.backend import cookie_transport
from app.auth.grants import AuthorizationCodeGrant
from app.auth.models import User
from app.auth.schemas import OAuth2ConsentRequest
from app.frontend.dependencies import (
    action_verified,
    get_optional_user,
    get_user,
    valid_consent,
)
from app.frontend.openid import discovery_document, jwks
from app.frontend.templating import templates
from app.oauth.dependencies import OAuthAccountsDep

router = APIRouter()


@router.get("/")
def index() -> Response:
    return RedirectResponse(url="/login")


@router.get("/register")
def register(
    request: Request,
    user: Annotated[User | None, Depends(get_optional_user)],
) -> Response:
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login")
def login(
    request: Request,
    user: Annotated[User | None, Depends(get_optional_user)],
) -> Response:
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse("authorize.html", {"request": request})


@router.get("/authorize")
async def authorize(
    request: Request,
    user: Annotated[User | None, Depends(get_optional_user)],
    consent: Annotated[OAuth2ConsentRequest, Depends(valid_consent)],
    authorization_code_grant: Annotated[AuthorizationCodeGrant, Depends()],
) -> Response:
    if user is None:
        request.session["consent"] = consent.model_dump(mode="json")
        return templates.TemplateResponse("authorize.html", {"request": request})
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


@router.get("/verify-action")
def verify_action(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(action_verified)],
    action: Literal["change-email", "change-password", "delete-account"],
) -> Response:
    if verified:
        return RedirectResponse(f"/{action}")
    return templates.TemplateResponse(
        "verify-action.html",
        {"request": request, "user": user},
    )


@router.get("/change-email")
def change_email(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(action_verified)],
) -> Any:
    if not verified:
        return RedirectResponse("/verify-action?action=change-email")
    return templates.TemplateResponse(
        "change-email.html",
        {"request": request, "user": user},
    )


@router.get("/change-password")
def change_password(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(action_verified)],
) -> Response:
    if not verified:
        return RedirectResponse("/verify-action?action=change-password")
    return templates.TemplateResponse(
        "change-password.html",
        {"request": request, "user": user},
    )


@router.get("/delete-account")
def delete_account(
    request: Request,
    user: Annotated[User, Depends(get_user)],
    verified: Annotated[bool, Depends(action_verified)],
) -> Response:
    if not verified:
        return RedirectResponse("/verify-action?action=delete-account")
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
