from typing import Any, Annotated
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Response, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse

from client.config import settings

app = FastAPI()


@app.get("/login")
def login(request: Request) -> Any:
    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "redirect_uri": request.url_for("callback"),
    }
    url = f"http://localhost:8012/authorize?{urlencode(params)}"
    return RedirectResponse(url=url)


@app.get("/callback")
def callback(code: str) -> Any:
    token_data = httpx.post(
        "http://localhost:8012/api/v1/token",
        json={
            "code": code,
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
        },
    )
    token = token_data.json()
    response = Response()
    response.set_cookie("access_token", token["access_token"])
    return response


def current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "No access token")
    response = httpx.get(
        "http://localhost:8012/api/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()


@app.get("/test")
def test(user: Annotated[dict[str, Any], Depends(current_user)]) -> Any:
    return user
