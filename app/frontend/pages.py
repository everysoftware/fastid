from typing import Any

from fastapi import APIRouter, Request, Response
from starlette import status
from starlette.responses import RedirectResponse

from app.auth.dependencies import UserDep
from app.authlib.dependencies import cookie_transport
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
def authorize(
    request: Request,
) -> Response:
    response = templates.TemplateResponse(
        "authorize.html", {"request": request}
    )
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
