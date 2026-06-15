from typing import Any

from fastid.auth.schemas import OpenID, TokenResponse
from fastid.core.schemas import BaseModel


class LoginResponse(BaseModel):
    token: TokenResponse
    token_raw: dict[str, Any]


class UserinfoResponse(BaseModel):
    userinfo: OpenID
    userinfo_raw: dict[str, Any]


class TelegramCallback(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TelegramWidget(BaseModel):
    bot_username: str
    callback_url: str
    scope: str = "write"
