from collections.abc import Callable, MutableMapping
from typing import Any, Protocol, Self

from auth365.schemas import OpenID, TokenResponse

from app.oauth.exceptions import OAuthProviderDisabledError, OAuthProviderNotFoundError
from app.oauth.schemas import ProviderMeta, RegistryMeta


class OAuth2Flow(Protocol):
    provider: str

    async def get_authorization_url(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str: ...

    async def authorize(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TokenResponse: ...

    async def userinfo(self, *args: Any, **kwargs: Any) -> OpenID: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...


class ProviderRegistry:
    def __init__(
        self,
        *,
        base_authorization_url: str,
        base_revoke_url: str,
    ) -> None:
        self.metadata = RegistryMeta()
        self.base_authorization_url = base_authorization_url
        self.base_revoke_url = base_revoke_url
        self._providers: MutableMapping[str, Callable[[], OAuth2Flow]] = {}

    def provider(
        self,
        name: str,
        *,
        title: str,
        icon: str,
        color: str,
        enabled: bool = True,
    ) -> Callable[[Callable[[], OAuth2Flow]], Callable[[], OAuth2Flow]]:
        def wrapper(
            factory: Callable[[], OAuth2Flow],
        ) -> Callable[[], OAuth2Flow]:
            meta = ProviderMeta(
                name=name,
                title=title,
                icon=icon,
                color=color,
                authorization_url=f"{self.base_authorization_url}/{name}",
                revoke_url=f"{self.base_revoke_url}/{name}",
                enabled=enabled,
            )
            self.metadata.providers[name] = meta
            self._providers[name] = factory
            return factory

        return wrapper

    def get(self, name: str) -> OAuth2Flow:
        if name not in self.metadata.providers:
            raise OAuthProviderNotFoundError()
        if not self.metadata.providers[name].enabled:
            raise OAuthProviderDisabledError()
        return self._providers[name]()
