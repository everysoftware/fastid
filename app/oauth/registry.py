from typing import MutableMapping, Callable

from app.oauth.schemas import ProviderMeta
from app.oauthlib.base import IOAuth2


class OAuthRegistry:
    def __init__(
        self,
        *,
        base_redirect_url: str,
        base_authorization_url: str,
        base_revoke_url: str,
    ) -> None:
        self.base_redirect_url = base_redirect_url
        self.base_authorization_url = base_authorization_url
        self.base_revoke_url = base_revoke_url

        self._meta: MutableMapping[str, ProviderMeta] = {}
        self._registry: MutableMapping[
            str, Callable[[ProviderMeta], IOAuth2]
        ] = {}

    @property
    def meta(self) -> MutableMapping[str, ProviderMeta]:
        return self._meta

    def provider(
        self, name: str, title: str, icon: str, color: str
    ) -> Callable[[Callable[[ProviderMeta], IOAuth2]], None]:
        def wrapper(factory: Callable[[ProviderMeta], IOAuth2]) -> None:
            meta = ProviderMeta(
                name=name,
                title=title,
                icon=icon,
                color=color,
                redirect_uri=f"{self.base_redirect_url}/{name}",
                authorization_url=f"{self.base_authorization_url}/{name}",
                revoke_url=f"{self.base_revoke_url}/{name}",
            )
            self._meta[name] = meta
            self._registry[name] = factory

        return wrapper

    def inspect(self, name: str) -> ProviderMeta:
        return self._meta[name]

    def begin(self, name: str) -> IOAuth2:
        return self._registry[name](self._meta[name])
