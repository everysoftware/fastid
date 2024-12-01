from typing import MutableMapping, Callable

from app.oauth.schemas import ProviderMeta
from app.oauthlib.base import OAuth2Flow
from app.oauthlib.exceptions import OAuth2Error


class ProviderRegistry:
    def __init__(
        self,
        *,
        base_authorization_url: str,
        base_revoke_url: str,
    ) -> None:
        self.base_authorization_url = base_authorization_url
        self.base_revoke_url = base_revoke_url

        self._meta: MutableMapping[str, ProviderMeta] = {}
        self._registry: MutableMapping[str, Callable[[], OAuth2Flow]] = {}

    @property
    def meta(self) -> MutableMapping[str, ProviderMeta]:
        return self._meta

    def provider(
        self,
        name: str,
        *,
        title: str,
        icon: str,
        color: str,
        enabled: bool = True,
    ) -> Callable[[Callable[[], OAuth2Flow]], None]:
        def wrapper(
            factory: Callable[[], OAuth2Flow],
        ) -> None:
            meta = ProviderMeta(
                name=name,
                title=title,
                icon=icon,
                color=color,
                authorization_url=f"{self.base_authorization_url}/{name}",
                revoke_url=f"{self.base_revoke_url}/{name}",
                enabled=enabled,
            )
            self._meta[name] = meta
            self._registry[name] = factory

        return wrapper

    def get(self, name: str) -> OAuth2Flow:
        if name not in self._registry:
            raise OAuth2Error(f"Provider {name} not found")
        if not self._meta[name].enabled:
            raise OAuth2Error(f"Provider {name} is disabled")
        return self._registry[name]()
