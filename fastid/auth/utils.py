from collections.abc import Mapping

from fastapi import Request
from fastlink.integrations.fastapi.transport import Transport

from fastid.auth.exceptions import NoTokenProvidedError


class AuthBus:
    transports: Mapping[str, Transport]

    def __init__(self, *transports: Transport, auto_error: bool = True) -> None:
        self.auto_error = auto_error
        self.transports = {t.scheme_name: t for t in transports}

    def parse_request(self, request: Request, *, auto_error: bool | None = None) -> str | None:
        if auto_error is None:
            auto_error = self.auto_error
        for transport in self.transports.values():
            token = transport.get_token(request)
            if token:
                return token
        if auto_error:
            raise NoTokenProvidedError
        return None

    def __call__(self, request: Request) -> str | None:
        return self.parse_request(request)
