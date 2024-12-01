from abc import ABC, abstractmethod
from typing import (
    Any,
    Sequence,
    Self,
)

from app.authlib.oauth import TokenResponse, OAuth2Callback
from app.authlib.openid import DiscoveryDocument
from app.oauthlib.schemas import OpenID


class OAuth2Flow(ABC):
    provider: str = NotImplemented
    default_scope: Sequence[str] = []

    @property
    @abstractmethod
    def discovery(self) -> DiscoveryDocument: ...

    @property
    @abstractmethod
    def token(self) -> TokenResponse: ...

    @abstractmethod
    def get_authorization_url(
        self,
        *,
        scope: Sequence[str] | None = None,
        redirect_uri: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str: ...

    @abstractmethod
    async def authorize(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TokenResponse: ...

    @abstractmethod
    async def userinfo(self) -> OpenID: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self, exc_type: Any, exc_value: Any, traceback: Any
    ) -> None: ...


class ImplicitFlow(OAuth2Flow, ABC):
    @abstractmethod
    async def authorize(
        self,
        callback: Any,
    ) -> TokenResponse: ...


class AuthorizationCodeFlow(OAuth2Flow, ABC):
    @abstractmethod
    async def authorize(
        self,
        callback: OAuth2Callback,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TokenResponse: ...
