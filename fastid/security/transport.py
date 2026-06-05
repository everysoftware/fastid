import abc
from abc import ABC
from typing import Literal

from fastapi import HTTPException, Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from starlette.responses import JSONResponse

from fastid.auth.schemas import TokenResponse


class Transport(ABC):
    def __init__(self, *, name: str, scheme_name: str) -> None:
        self.name = name
        self.scheme_name = scheme_name

    @abc.abstractmethod
    def get_token(self, request: Request) -> str | None: ...

    @abc.abstractmethod
    def set_token(self, response: Response, token: str) -> Response: ...

    @abc.abstractmethod
    def delete_token(self, response: Response) -> Response: ...

    def get_login_response(self, token: TokenResponse) -> Response:
        response = JSONResponse(content=token.model_dump())
        assert token.access_token is not None
        self.set_token(response, token.access_token)
        return response

    def get_logout_response(self) -> Response:
        response = Response()
        self.delete_token(response)
        return response

    def __call__(self, request: Request) -> str:
        token = self.get_token(request)
        if token is None:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token


class HeaderTransport(Transport):
    def __init__(
        self,
        *,
        name: str = "Authorization",
        scheme_name: str = "BearerHeader",
    ) -> None:
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

    def delete_token(self, response: Response) -> Response:
        del response.headers[self.name]
        return response


class CookieTransport(Transport):
    def __init__(  # noqa: PLR0913
        self,
        *,
        name: str = "access_token",
        scheme_name: str = "BearerCookie",
        httponly: bool = True,
        max_age: int = 3600,
        secure: bool = False,
        samesite: Literal["lax", "strict", "none"] = "lax",
    ) -> None:
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

    def delete_token(self, response: Response) -> Response:
        response.delete_cookie(
            key=self.name,
            secure=self.secure,
            samesite=self.samesite,
        )
        return response
