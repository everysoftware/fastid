from fastapi import APIRouter, Request, Response

from app.utils.templating import templates

router = APIRouter()


@router.get("/authorize")
def authorize(
    request: Request,
) -> Response:
    response = templates.TemplateResponse("login.html", {"request": request})
    return response


@router.get("/me")
def me(
    request: Request,
) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/oauth-callback")
def callback(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})
