from collections.abc import Callable, MutableMapping

from fastlink import SSOBase

from fastid.oauth.exceptions import OAuthProviderDisabledError, OAuthProviderNotFoundError
from fastid.oauth.schemas import SSOMeta, SSORegistryMeta


class SSORegistry:  # pragma: nocover
    def __init__(
        self,
        *,
        base_authorization_url: str,
        base_revoke_url: str,
    ) -> None:
        self.metadata = SSORegistryMeta()
        self.base_authorization_url = base_authorization_url
        self.base_revoke_url = base_revoke_url
        self._providers: MutableMapping[str, Callable[[], SSOBase]] = {}

    def provider(
        self,
        name: str,
        *,
        title: str,
        icon: str,
        color: str,
        enabled: bool = True,
    ) -> Callable[[Callable[[], SSOBase]], Callable[[], SSOBase]]:
        def wrapper(
            factory: Callable[[], SSOBase],
        ) -> Callable[[], SSOBase]:
            meta = SSOMeta(
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

    def get(self, name: str) -> SSOBase:
        if name not in self.metadata.providers:
            raise OAuthProviderNotFoundError
        if not self.metadata.providers[name].enabled:
            raise OAuthProviderDisabledError
        return self._providers[name]()
