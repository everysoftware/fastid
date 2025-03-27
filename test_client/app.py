from typing import Annotated, Any
from urllib.parse import urlencode

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from test_client.config import settings

app = FastAPI()


@app.get("/login")
def login(request: Request) -> Any:
    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "redirect_uri": request.url_for("callback"),
    }
    url = f"{settings.fastid_url}/authorize?{urlencode(params)}"
    return RedirectResponse(url=url)


@app.get("/callback")
def callback(code: str) -> Any:
    token_data = httpx.post(
        f"{settings.fastid_url}/api/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "code": code,
        },
    )
    token = token_data.json()
    response = Response(content="You are now logged in!")
    response.set_cookie("access_token", token["access_token"], httponly=True)
    return response


def current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "No access token")
    response = httpx.get(
        f"{settings.fastid_url}/api/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()  # type: ignore[no-any-return]


@app.get("/test")
def test(user: Annotated[dict[str, Any], Depends(current_user)]) -> Any:
    return user
