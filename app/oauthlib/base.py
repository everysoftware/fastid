from abc import ABC, abstractmethod
from typing import (
    Any,
    ClassVar,
    Sequence,
    Self,
)
from urllib.parse import urlencode

import httpx

from app.authlib.oauth import TokenResponse, OAuth2Callback
from app.authlib.openid import DiscoveryDocument
from app.main import logging
from app.oauthlib.exceptions import OAuth2Error
from app.oauthlib.pkce import get_pkce_challenge_pair
from app.oauthlib.schemas import OpenID
from app.oauthlib.utils import generate_random_state

logger = logging.get_logger(__name__)


class IOAuth2(ABC):
    provider: ClassVar[str] = NotImplemented
    default_scope: ClassVar[Sequence[str]] = []
    use_state: ClassVar[bool] = True
    use_pkce: ClassVar[bool] = False
    code_challenge_method: ClassVar[str] = "S256"
    code_challenge_length: ClassVar[int] = 96

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        scope: Sequence[str] | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or self.default_scope
        self.is_authorized = False

    @property
    @abstractmethod
    def discovery(self) -> DiscoveryDocument:
        """
        Returns the discovery document containing useful URLs.

        Returns:
            A dictionary containing important endpoints like authorization, token and userinfo.
        """
        ...

    @property
    @abstractmethod
    def token(self) -> TokenResponse:
        """
        Returns the token response from the OAuth provider.

        Returns:
            The token response containing access token, refresh token, etc.
        """

    @abstractmethod
    def get_authorization_url(
        self,
        *,
        scope: list[str] | None = None,
        redirect_uri: str | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str: ...

    @abstractmethod
    async def authorize(
        self,
        callback: Any,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TokenResponse:
        """
        Login to the OAuth provider and get the bearer token.

        Args:
            callback: The callback URL with code and other params.
            params: Additional query parameters to add to the token request.
            headers: Additional headers to add to the token request.

        Returns:
            The bearer token with access token and other details.
        """
        ...

    @abstractmethod
    async def userinfo(
        self,
        *,
        headers: dict[str, str] | None = None,
    ) -> OpenID:
        """
        Get user information from the userinfo endpoint.

        Args:
            headers: Additional headers to add to the request.

        Returns:
            The user information in a standardized format.
        """
        ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[Exception], exc_value: Exception, traceback: Any
    ) -> None: ...


class HTTPXOAuth2(IOAuth2, ABC):
    _generated_state: str | None = None
    _code_challenge: str | None = None
    _code_verifier: str | None = None
    _token: TokenResponse | None = None
    _discovery: DiscoveryDocument | None = None
    _client: httpx.AsyncClient | None = None

    @abstractmethod
    async def discover(self) -> DiscoveryDocument:
        """Retrieves the discovery document containing useful URLs.

        Returns:
            A dictionary containing important endpoints like authorization, token and userinfo.
        """
        ...

    @abstractmethod
    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        """Converts a response from the provider's user info endpoint to an OpenID object.

        Args:
            response: The response from the user info endpoint.

        Returns:
            The user information in a standardized format.
        """
        ...

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
        if self._client is None:
            raise OAuth2Error(
                "HTTP client is not available. Please use the async context manager."
            )
        return self._client

    def get_authorization_url(
        self,
        *,
        scope: list[str] | None = None,
        redirect_uri: str | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        if self.use_state:
            self._generated_state = generate_random_state()
        if self.use_pkce:
            self._code_verifier, self._code_challenge = (
                get_pkce_challenge_pair(self.code_challenge_length)
            )
        params = params or {}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise OAuth2Error(
                "redirect_uri must be provided, either at construction or request time"
            )
        if self.use_pkce:
            params |= {
                "code_challenge": self._code_challenge,
                "code_challenge_method": self.code_challenge_method,
            }
        if self.use_state:
            params |= {"state": state or self._generated_state}
        request_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope or self.scope),
            **params,
        }
        return f"{self.discovery.authorization_endpoint}?{urlencode(request_params)}"

    async def authorize(
        self,
        callback: OAuth2Callback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TokenResponse:
        request = self._prepare_token_request(
            callback, params=params, headers=headers
        )
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with self.client as client:
            response = await client.send(
                request,
                auth=auth,
            )
            content = response.json()
            if response.status_code < 200 or response.status_code > 299:
                raise OAuth2Error("Authorization failed: %s", content)
            self._token = TokenResponse(
                access_token=content.get("access_token"),
                refresh_token=content.get("refresh_token"),
                id_token=content.get("id_token"),
                expires_in=content.get("expires_in"),
                token_type=content.get("token_type", "Bearer"),
                scope=content.get(
                    "scope", callback.scope or " ".join(self.scope)
                ),
            )
            self.is_authorized = True
            return self._token

    async def userinfo(
        self,
        *,
        headers: dict[str, Any] | None = None,
    ) -> OpenID:
        headers = headers or {}
        headers |= {
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.discovery.userinfo_endpoint, headers=headers
            )
            content = response.json()
            if response.status_code < 200 or response.status_code > 299:
                raise OAuth2Error("Getting userinfo failed: %s", content)
            return await self.openid_from_response(content)

    async def __aenter__(self) -> Self:
        if self._discovery is None:
            self._discovery = await self.discover()
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self

    async def __aexit__(
        self, exc_type: type[Exception], exc_value: Exception, traceback: Any
    ) -> None:
        self._token = None
        self.is_authorized = False

    def _prepare_token_request(
        self,
        callback: OAuth2Callback,
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
            self.discovery.token_endpoint,
            data=body,
            headers=headers,
        )
