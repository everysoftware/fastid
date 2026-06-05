from collections.abc import Callable, MutableMapping

from fastid.integrations.base.oauth import OAuth2Client
from fastid.oauth.exceptions import OAuthProviderNotFoundError


class OAuth2Registry:  # pragma: nocover
    def __init__(self) -> None:
        self._providers: MutableMapping[str, Callable[[], OAuth2Client]] = {}

    def provider(
        self,
        name: str,
    ) -> Callable[[Callable[[], OAuth2Client]], Callable[[], OAuth2Client]]:
        def wrapper(
            factory: Callable[[], OAuth2Client],
        ) -> Callable[[], OAuth2Client]:
            self._providers[name] = factory
            return factory

        return wrapper

    def get(self, name: str) -> OAuth2Client:
        if name not in self._providers:
            raise OAuthProviderNotFoundError
        return self._providers[name]()
