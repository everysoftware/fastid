from typing import Any, Annotated

from fastapi import APIRouter, Request, Response, Depends, status
from fastapi.responses import RedirectResponse

from app.api.exceptions import Unauthorized
from app.auth.dependencies import AuthDep
from app.auth.models import User
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.dependencies import cookie_transport
from app.frontend.dependencies import valid_consent, get_user
from app.frontend.templating import templates
from app.oauth.dependencies import OAuthAccountsDep

router = APIRouter()


@router.get("/")
def index() -> Response:
    return RedirectResponse(url="/login")


@router.get("/register")
def register(
    request: Request,
) -> Response:
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login")
def login(
    request: Request,
    user: Annotated[User | None, Depends(get_user)],
) -> Response:
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse("authorize.html", {"request": request})


@router.get("/authorize")
async def authorize(
    auth: AuthDep,
    request: Request,
    user: Annotated[User | None, Depends(get_user)],
    consent: Annotated[OAuth2ConsentRequest, Depends(valid_consent)],
) -> Response:
    if user is None:
        request.session["consent"] = consent.model_dump(mode="json")
        return templates.TemplateResponse(
            "authorize.html", {"request": request}
        )
    else:
        # User is authenticated, redirect to specified redirect URI with code
        request.session.clear()
        redirect_uri = await auth.approve_consent_request(consent, user.id)
        response = RedirectResponse(redirect_uri)
    return response


@router.get("/profile")
async def profile(
    request: Request,
    oauth_accounts: OAuthAccountsDep,
    user: Annotated[User | None, Depends(get_user)],
) -> Response:
    if user is None:
        raise Unauthorized()
    page = await oauth_accounts.paginate(user)
    connected = {a.provider for a in page.items}
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "connected_providers": connected},
    )


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    response = RedirectResponse(url="/login")
    cookie_transport.delete_token(response)
    return response
