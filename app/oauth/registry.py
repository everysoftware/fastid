from typing import MutableMapping, Callable

from app.oauth.schemas import ProviderMeta, RegistryMeta
from app.oauthlib.base import OAuth2Flow
from app.oauthlib.exceptions import OAuth2Error


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
            raise OAuth2Error(f"Provider {name} not found")
        if not self.metadata.providers[name].enabled:
            raise OAuth2Error(f"Provider {name} is disabled")
        return self._providers[name]()
