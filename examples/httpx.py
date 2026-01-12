from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from examples.config import settings

app = FastAPI()


@app.get("/login")
def login(request: Request) -> Any:
    params = {
        "response_type": "code",
        "client_id": settings.fastid_client_id,
        "redirect_uri": request.url_for("callback"),
        "scope": "openid",
    }
    url = f"{settings.fastid_url}/authorize?{urlencode(params)}"
    return RedirectResponse(url=url)


@app.get("/callback")
def callback(code: str) -> Any:
    response = httpx.post(
        f"{settings.fastid_url}/api/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": settings.fastid_client_id,
            "client_secret": settings.fastid_client_secret,
            "code": code,
        },
    )
    token = response.json()["access_token"]
    response = httpx.get(
        f"{settings.fastid_url}/api/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()
