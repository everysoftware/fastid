from typing import Literal, Annotated

from fastapi import APIRouter, Request, Response, Depends
from pydantic import AnyHttpUrl

from app.auth.dependencies import UserDep
from app.apps.dependencies import get_oauth_client, valid_redirect_uri
from app.apps.schemas import AppDTO
from app.utils.templating import templates

router = APIRouter()


@router.get("/authorize")
def authorize(
    request: Request,
    user: UserDep,
    client: Annotated[AppDTO, Depends(get_oauth_client)],
    response_type: Literal["code"],
    redirect_uri: Annotated[AnyHttpUrl, Depends(valid_redirect_uri)],
    state: str | None = None,
) -> Response:
    response = templates.TemplateResponse("login.html", {"request": request})
    return response


@router.get("/me")
def me(
    request: Request,
    user: UserDep,
    client: Annotated[AppDTO, Depends(get_oauth_client)],
    response_type: Literal["code"],
    redirect_uri: Annotated[AnyHttpUrl, Depends(valid_redirect_uri)],
    state: str | None = None,
) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/oauth-callback")
def callback(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})
