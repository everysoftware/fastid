import datetime
import hashlib
import hmac
from typing import Any
from urllib.parse import urlencode

from aiogram import Bot

from app.oauthlib.exceptions import OAuth2Error
from app.oauthlib.interfaces import IOAuth2
from app.oauthlib.schemas import (
    OpenID,
    AnyUrl,
    DiscoveryDocument,
    OAuthBearerToken,
    TelegramCallback,
)
from app.oauthlib.utils import replace_localhost


class TelegramOAuth(IOAuth2):
    provider = "telegram"
    scope = ["write"]
    expires_in: int = 5 * 60

    _bot: Bot
    _callback: TelegramCallback | None = None

    def __init__(
        self,
        bot_token: str,
        redirect_uri: AnyUrl | None = None,
        scope: list[str] | None = None,
        *,
        expires_in: int = 5 * 60,
    ):
        self._bot = Bot(token=bot_token)
        super().__init__(
            str(self._bot.id), self._bot.token, redirect_uri, scope
        )
        self.expires_in = expires_in

    async def discover(self) -> DiscoveryDocument:
        return DiscoveryDocument(
            authorization_endpoint="https://oauth.telegram.org/auth"
        )

    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        first_name, last_name = (
            response["first_name"],
            response.get("last_name"),
        )
        display_name = (
            f"{first_name} {last_name}" if first_name else first_name
        )
        return OpenID(
            id=str(response["id"]),
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            picture=response.get("photo_url"),
            provider=self.provider,
        )

    async def login(
        self,
        *,
        redirect_uri: AnyUrl | None = None,
        params: dict[str, Any] | None = None,
        state: str | None = None,
    ) -> str:
        params = params or {}
        redirect_uri = replace_localhost(redirect_uri or self.redirect_uri)
        login_params = {
            "bot_id": self._bot.id,
            "origin": redirect_uri,
            "request_access": self.scope,
            **params,
        }
        return f"{await self.authorization_endpoint}?{urlencode(login_params)}"

    async def callback(
        self,
        callback: TelegramCallback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> OAuthBearerToken:
        self._callback = callback
        response = callback.model_dump()
        code_hash = response.pop("hash")
        data_check_string = "\n".join(
            sorted(f"{k}={v}" for k, v in response.items())
        )
        computed_hash = hmac.new(
            hashlib.sha256(self.client_secret.encode()).digest(),
            data_check_string.encode(),
            "sha256",
        ).hexdigest()
        if not hmac.compare_digest(computed_hash, code_hash):
            raise OAuth2Error("Invalid Telegram auth data: hash mismatch")
        dt = datetime.datetime.fromtimestamp(
            response["auth_date"], tz=datetime.UTC
        )
        now = datetime.datetime.now(tz=datetime.UTC)
        if now - dt > datetime.timedelta(seconds=self.expires_in):
            raise OAuth2Error("Telegram auth data expired")
        self._token = OAuthBearerToken(access_token=callback.hash)
        return self.token

    async def get_user_raw(
        self,
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self._callback is None:
            raise OAuth2Error("Callback data is missing")
        return self._callback.model_dump()
