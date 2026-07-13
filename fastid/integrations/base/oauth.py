from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Self,
)
from urllib.parse import urlencode

import httpx

from fastid.auth.schemas import DiscoveryDocument, OAuth2Callback, OpenID, ProviderMeta, TokenResponse
from fastid.integrations.constants import MAX_SUCCESS_CODE, MIN_SUCCESS_CODE
from fastid.integrations.exceptions import (
    AuthorizationError,
    ClientError,
    DiscoveryError,
    RedirectURIError,
    StateError,
    TokenError,
    UserinfoError,
)
from fastid.integrations.schemas import LoginResponse, UserinfoResponse
from fastid.integrations.utils import generate_pkce_challenge, generate_pkce_verifier, generate_random_state


class OAuth2Client:
    default_meta: ClassVar[ProviderMeta]
    default_use_pkce: ClassVar[bool] = False
    pkce_challenge_method: ClassVar[str] = "S256"
    use_client_secret: ClassVar[bool] = True

    def __init__(  # noqa: PLR0913
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        scope: Sequence[str] | None = None,
        meta: ProviderMeta | None = None,
        use_pkce: bool | None = None,
    ) -> None:
        self.meta = meta or self.default_meta
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.use_state = self.meta.use_state
        self.use_pkce = self.default_use_pkce if use_pkce is None else use_pkce
        self.discovery_url = self.meta.discovery_url
        self._discovery = None

        scope = scope or self.meta.scope
        assert scope is not None
        self.scope = scope

        if self.meta.discovery is not None:
            self._discovery = self.meta.discovery

        if self.meta.server_url is not None:
            self.discovery_url = f"{self.meta.server_url}/.well-known/openid-configuration"

        self._token: TokenResponse | None = None
        self._client: httpx.AsyncClient | None = None

    @property
    def discovery(self) -> DiscoveryDocument:
        if self._discovery is None:
            msg = "Discovery document is not available. Please discover first."
            raise DiscoveryError(msg)
        return self._discovery

    @property
    def token(self) -> TokenResponse:
        if not self._token:
            msg = "Token is not available. Please authorize first."
            raise TokenError(msg)
        return self._token

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            msg = "Client is not available. Please enter the context."
            raise ClientError(msg)
        return self._client

    async def convert_token(self, response: dict[str, Any]) -> TokenResponse:
        return TokenResponse.model_validate(response)

    async def convert_userinfo(self, response: dict[str, Any]) -> OpenID:  # noqa: ARG002
        return OpenID()

    async def discover(self) -> DiscoveryDocument:
        assert self.discovery_url is not None
        response = await self.client.get(self.discovery_url)
        return DiscoveryDocument.model_validate(response.json())

    async def login_url(
        self,
        *,
        redirect_uri: str | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        params = params or {}
        if self.use_state or self.use_pkce:
            state = state or generate_random_state()
            params |= {"state": state}
        if self.use_pkce:
            assert state is not None
            params |= {
                "code_challenge": generate_pkce_challenge(generate_pkce_verifier(state, self.client_secret)),
                "code_challenge_method": self.pkce_challenge_method,
            }
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            msg = "redirect_uri must be provided, either at construction or request time"
            raise RedirectURIError(msg)
        request_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "redirect_uri": redirect_uri,
            **params,
        }
        return f"{self.discovery.authorization_endpoint}?{urlencode(request_params)}"

    async def login(
        self,
        callback: OAuth2Callback,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> LoginResponse:
        request = self._prepare_token_request(callback, body=body, headers=headers)
        auth = httpx.BasicAuth(self.client_id, self.client_secret) if self.use_client_secret else None
        response = await self.client.send(
            request,
            auth=auth,
        )
        content = response.json()
        if response.status_code < MIN_SUCCESS_CODE or response.status_code > MAX_SUCCESS_CODE:
            msg = "Authorization failed: %s"
            raise AuthorizationError(msg, content)
        token = await self.convert_token(content)
        self._token = token
        return LoginResponse(token=token, token_raw=content)

    async def userinfo(self) -> UserinfoResponse:
        assert self.discovery.userinfo_endpoint is not None
        headers = {
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        }
        response = await self.client.get(self.discovery.userinfo_endpoint, headers=headers)
        content = response.json()
        if response.status_code < MIN_SUCCESS_CODE or response.status_code > MAX_SUCCESS_CODE:
            msg = "Getting userinfo failed: %s"
            raise UserinfoError(msg, content)
        userinfo = await self.convert_userinfo(content)
        return UserinfoResponse(userinfo=userinfo, userinfo_raw=content)

    async def callback(self, callback: OAuth2Callback) -> UserinfoResponse:
        await self.login(callback)
        return await self.userinfo()

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
                msg = "State was not found in the callback"
                raise StateError(msg)
            body |= {"state": callback.state}
        if self.use_pkce:
            if not callback.state:
                msg = "PKCE code verifier was not found in the callback state"
                raise StateError(msg)
            body |= {"code_verifier": generate_pkce_verifier(callback.state, self.client_secret)}
        body = {
            "grant_type": "authorization_code",
            "code": callback.code,
            "redirect_uri": callback.redirect_uri or self.redirect_uri,
            "client_id": self.client_id,
            **body,
        }
        if self.use_client_secret:
            body["client_secret"] = self.client_secret
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
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._token = None
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def __call__(self) -> AsyncIterator[Self]:
        async with self:
            yield self
