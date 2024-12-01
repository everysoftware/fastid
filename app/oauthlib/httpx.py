from abc import ABC, abstractmethod
from typing import Any, Self, Sequence
from urllib.parse import urlencode

import httpx

from app.authlib.oauth import TokenResponse, OAuth2Callback
from app.authlib.openid import DiscoveryDocument
from app.oauthlib.base import AuthorizationCodeFlow
from app.oauthlib.exceptions import OAuth2Error
from app.oauthlib.schemas import OpenID
from app.oauthlib.utils import generate_random_state


class HTTPXOAuth2(AuthorizationCodeFlow, ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        scope: Sequence[str] | None = None,
        *,
        use_state: bool = True,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or self.default_scope
        self.use_state = use_state

        self._token: TokenResponse | None = None
        self._discovery: DiscoveryDocument | None = None
        self._client: httpx.AsyncClient | None = None

    @abstractmethod
    async def discover(self) -> DiscoveryDocument: ...

    @abstractmethod
    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID: ...

    @property
    def discovery(self) -> DiscoveryDocument:
        if self._discovery is None:
            raise OAuth2Error(
                "Discovery document is not available. Please discover first."
            )
        return self._discovery

    @property
    def token(self) -> TokenResponse:
        if not self._token:
            raise OAuth2Error(
                "Token is not available. Please authorize first."
            )
        return self._token

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise OAuth2Error(
                "Client is not available. Please enter the context."
            )
        return self._client

    def get_authorization_url(
        self,
        *,
        scope: Sequence[str] | None = None,
        redirect_uri: str | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        params = params or {}
        if self.use_state:
            params |= {"state": state or generate_random_state()}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise OAuth2Error(
                "redirect_uri must be provided, either at construction or request time"
            )
        request_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": " ".join(scope or self.scope),
            "redirect_uri": redirect_uri,
            **params,
        }
        return f"{self.discovery.authorization_endpoint}?{urlencode(request_params)}"

    async def authorize(
        self,
        callback: OAuth2Callback,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TokenResponse:
        request = self._prepare_token_request(
            callback, body=body, headers=headers
        )
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        response = await self.client.send(
            request,
            auth=auth,
        )
        content = response.json()
        if response.status_code < 200 or response.status_code > 299:
            raise OAuth2Error("Authorization failed: %s", content)
        self._token = TokenResponse.model_validate(content)
        return self._token

    async def userinfo(self) -> OpenID:
        assert self.discovery.userinfo_endpoint is not None
        headers = {
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        }
        response = await self.client.get(
            self.discovery.userinfo_endpoint, headers=headers
        )
        content = response.json()
        if response.status_code < 200 or response.status_code > 299:
            raise OAuth2Error("Getting userinfo failed: %s", content)
        return await self.openid_from_response(content)

    def _prepare_token_request(
        self,
        callback: OAuth2Callback,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Request:
        assert self.discovery.token_endpoint is not None
        body = body or {}
        headers = headers or {}
        headers |= {"Content-Type": "application/x-www-form-urlencoded"}
        if self.use_state:
            if not callback.state:
                raise OAuth2Error("State was not found in the callback")
            body |= {"state": callback.state}
        body = {
            "grant_type": "authorization_code",
            "code": callback.code,
            "redirect_uri": callback.redirect_uri or self.redirect_uri,
            **body,
        }
        return httpx.Request(
            "post",
            self.discovery.token_endpoint,
            data=body,
            headers=headers,
        )

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient()
        await self._client.__aenter__()
        if self._discovery is None:
            self._discovery = await self.discover()
        return self

    async def __aexit__(
        self, exc_type: Any, exc_value: Any, traceback: Any
    ) -> None:
        self._token = None
        await self.client.__aexit__(exc_type, exc_value, traceback)
