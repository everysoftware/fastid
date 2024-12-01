from abc import ABC, abstractmethod
from typing import (
    Any,
    ClassVar,
    Sequence,
    Self,
)

from app.authlib.oauth import TokenResponse, OAuth2Callback
from app.authlib.openid import DiscoveryDocument
from app.oauthlib.schemas import OpenID


class OAuth2Flow(ABC):
    provider: ClassVar[str] = NotImplemented
    default_scope: ClassVar[Sequence[str]] = []

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
        state: str | None = None,
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
        self, exc_type: type[Exception], exc_value: Exception, traceback: Any
    ) -> None: ...


class ImplicitFlow(OAuth2Flow, ABC):
    @abstractmethod
    async def authorize(
        self,
        callback: Any,
    ) -> TokenResponse: ...


class AuthorizationCodeFlow(OAuth2Flow, ABC):
    use_state: ClassVar[bool] = True
    use_pkce: ClassVar[bool] = False
    code_challenge_method: ClassVar[str] = "S256"
    code_challenge_length: ClassVar[int] = 96

    @abstractmethod
    async def authorize(
        self,
        callback: OAuth2Callback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TokenResponse: ...
