from typing import Any, Annotated

from fastapi import APIRouter, Request, Response, Depends, status
from fastapi.responses import RedirectResponse

from app.api.exceptions import ClientError
from app.auth.dependencies import UserDep, AuthDep
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.dependencies import cookie_transport, auth_bus
from app.frontend.templating import templates

router = APIRouter()


@router.get("/")
def index() -> Response:
    return RedirectResponse(url="/authorize")


@router.get("/register")
def register(
    request: Request,
) -> Response:
    response = templates.TemplateResponse(
        "register.html", {"request": request}
    )
    return response


@router.get("/authorize")
async def authorize(
    request: Request,
    consent: Annotated[OAuth2ConsentRequest, Depends()],
    auth: AuthDep,
) -> Response:
    # Check if consent is saved in cookies
    if consent.redirect_uri is None:
        consent_data = request.session.get("consent")
        if consent_data is not None:
            consent = OAuth2ConsentRequest.model_validate(consent_data)
        if consent.redirect_uri is None:
            consent.redirect_uri = "/profile"

    # Check if user is already authenticated
    token = auth_bus.parse_request(request, auto_error=False)
    response: Response
    if token is None:
        token = ""
    try:
        await auth.get_userinfo(token)
    except ClientError:
        response = templates.TemplateResponse(
            "authorize.html", {"request": request}
        )
        request.session["consent"] = consent.model_dump(mode="json")
    else:
        request.session.clear()
        response = RedirectResponse(consent.redirect_uri)
    return response


@router.get("/profile")
def profile(
    request: Request,
    user: UserDep,
) -> Response:
    response = templates.TemplateResponse(
        "profile.html", {"request": request, "user": user}
    )
    return response


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    response = RedirectResponse(url="/authorize")
    cookie_transport.delete_token(response)
    return response
