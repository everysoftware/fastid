import abc
from abc import ABC
from typing import Mapping, Literal

from fastapi import Response
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.authlib.exceptions import NoTokenProvided


class Transport(ABC):
    def __init__(self, *, name: str, scheme_name: str):
        self.name = name
        self.scheme_name = scheme_name

    @abc.abstractmethod
    def get_token(self, request: Request) -> str | None: ...

    @abc.abstractmethod
    def set_token(self, response: Response, token: str) -> Response: ...


class HeaderTransport(Transport):
    def __init__(
        self,
        *,
        name: str = "Authorization",
        scheme_name: str = "BearerHeader",
    ):
        super().__init__(name=name, scheme_name=scheme_name)

    def get_token(self, request: Request) -> str | None:
        authorization = request.headers.get(self.name)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            return None
        return param

    def set_token(self, response: Response, token: str) -> Response:
        response.headers[self.name] = f"Bearer {token}"
        return response


class CookieTransport(Transport):
    def __init__(
        self,
        *,
        name: str = "fastidaccesstoken",
        scheme_name: str = "BearerCookie",
        httponly: bool = True,
        max_age: int | None = None,
        secure: bool = False,
        samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        super().__init__(name=name, scheme_name=scheme_name)
        self.httponly = httponly
        self.max_age = max_age
        self.secure = secure
        self.samesite = samesite

    def get_token(self, request: Request) -> str | None:
        return request.cookies.get(self.name)

    def set_token(self, response: Response, token: str) -> Response:
        response.set_cookie(
            key=self.name,
            value=token,
            httponly=self.httponly,
            max_age=self.max_age,
            secure=self.secure,
            samesite=self.samesite,
        )
        return response


class AuthBus:
    transports: Mapping[str, Transport]

    def __init__(self, *transports: Transport, auto_error: bool = True):
        self.auto_error = auto_error
        self.transports = {t.scheme_name: t for t in transports}

    def parse_request(self, request: Request) -> str | None:
        for transport in self.transports.values():
            token = transport.get_token(request)
            if token:
                return token
        if self.auto_error:
            raise NoTokenProvided()
        return None

    def __call__(self, request: Request) -> str | None:
        return self.parse_request(request)