from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from fastlink import FastLink
from fastlink.schemas import OAuth2Callback, ProviderMeta

from examples.config import settings

app = FastAPI()
fastid = FastLink(
    ProviderMeta(server_url=settings.fastid_url, scope=["openid"]),
    settings.client_id,
    settings.client_secret,
    "http://localhost:8000/callback",
)


@app.get("/login")
async def login() -> Any:
    async with fastid:
        url = await fastid.login_url()
        return RedirectResponse(url=url)


@app.get("/callback")
async def callback(call: Annotated[OAuth2Callback, Depends()]) -> Any:
    async with fastid:
        return await fastid.callback_raw(call)
