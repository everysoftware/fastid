from abc import ABC
from typing import (
    Any,
)
from urllib.parse import urlencode

import httpx

from app.main import logging
from app.oauthlib.exceptions import OAuth2Error
from app.oauthlib.interfaces import IOAuth2
from app.oauthlib.pkce import get_pkce_challenge_pair
from app.oauthlib.schemas import (
    OAuthCallback,
    OAuthBearerToken,
    AnyUrl,
)
from app.oauthlib.utils import generate_random_state

logger = logging.get_logger(__name__)


class BaseOAuth2(IOAuth2, ABC):
    use_state: bool = True
    use_pkce: bool = False
    code_challenge_method: str = "S256"
    code_challenge_length: int = 96

    generated_state: str | None = None
    code_challenge: str | None = None
    code_verifier: str | None = None

    async def login(
        self,
        *,
        scope: list[str] | None = None,
        redirect_uri: AnyUrl | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        if self.use_state:
            self.generated_state = generate_random_state()
        if self.use_pkce:
            self.code_verifier, self.code_challenge = get_pkce_challenge_pair(
                self.code_challenge_length
            )
        params = params or {}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise OAuth2Error(
                "redirect_uri must be provided, either at construction or request time"
            )
        if self.use_pkce:
            params |= {
                "code_challenge": self.code_challenge,
                "code_challenge_method": self.code_challenge_method,
            }
        if self.use_state:
            params |= {"state": state or self.generated_state}
        request_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope or self.scope),
            **params,
        }
        return (
            f"{await self.authorization_endpoint}?{urlencode(request_params)}"
        )

    async def callback(
        self,
        callback: OAuthCallback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> OAuthBearerToken:
        request = await self._prepare_token_request(
            callback, params=params, headers=headers
        )
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with self._get_client() as client:
            response = await client.send(
                request,
                auth=auth,
            )
            content = response.json()
            if response.status_code < 200 or response.status_code > 299:
                raise OAuth2Error("Failed to get token", content)
            self._token = OAuthBearerToken(
                access_token=content.get("access_token"),
                refresh_token=content.get("refresh_token"),
                id_token=content.get("id_token"),
                expires_in=content.get("expires_in"),
                token_type=content.get("token_type", "Bearer"),
                scope=content.get(
                    "scope", callback.scope or " ".join(self.scope)
                ),
            )
            return self._token

    async def get_user_raw(
        self,
        *,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = headers or {}
        headers |= {
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                await self.userinfo_endpoint, headers=headers
            )
            return response.json()  # type: ignore[no-any-return]

    def _get_client(self) -> httpx.AsyncClient:  # noqa
        return httpx.AsyncClient()

    async def _prepare_token_request(
        self,
        callback: OAuthCallback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Request:
        params = params or {}
        headers = headers or {}
        headers |= {"Content-Type": "application/x-www-form-urlencoded"}
        if self.use_state:
            if not callback.state:
                raise OAuth2Error("State was not found in the callback")
            params |= {"state": callback.state}
        if self.use_pkce:
            if not callback.code_verifier:
                raise OAuth2Error(
                    "PKCE code verifier was not found in the callback"
                )
            params |= {"code_verifier": callback.code_verifier}
        body = {
            "grant_type": "authorization_code",
            "code": callback.code,
            "redirect_uri": callback.redirect_uri or self.redirect_uri,
            **params,
        }
        return httpx.Request(
            "post",
            await self.token_endpoint,
            data=body,
            headers=headers,
        )
