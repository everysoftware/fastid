from typing import Any, Annotated

from fastapi import APIRouter, Request, Response, Depends, status
from fastapi.responses import RedirectResponse

from app.api.exceptions import ClientError
from app.auth.dependencies import UserDep, AuthDep
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.dependencies import cookie_transport, token_backend
from app.base.types import UUID
from app.frontend.dependencies import valid_consent
from app.frontend.templating import templates

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
async def login(
    request: Request,
) -> Response:
    token = cookie_transport.get_token(request)
    if token is None:
        return templates.TemplateResponse(
            "authorize.html", {"request": request}
        )
    return RedirectResponse(url="/profile")


def get_consent_response(
    request: Request, consent: OAuth2ConsentRequest
) -> Response:
    request.session["consent"] = consent.model_dump(mode="json")
    return templates.TemplateResponse("authorize.html", {"request": request})


@router.get("/authorize")
async def authorize(
    auth: AuthDep,
    request: Request,
    consent: Annotated[OAuth2ConsentRequest, Depends(valid_consent)],
) -> Response:
    token = cookie_transport.get_token(request)
    if token is None:
        return get_consent_response(request, consent)
    try:
        payload = token_backend.validate_at(token)
    except ClientError:
        return get_consent_response(request, consent)
    else:
        # User is authenticated, redirect to specified redirect URI with code
        request.session.clear()
        redirect_uri = await auth.approve_consent_request(
            consent, UUID(payload.sub)
        )
        response = RedirectResponse(redirect_uri)
    return response


@router.get("/profile")
def profile(
    request: Request,
    user: UserDep,
) -> Response:
    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": user}
    )


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    response = RedirectResponse(url="/login")
    cookie_transport.delete_token(response)
    return response
