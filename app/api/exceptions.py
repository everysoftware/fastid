from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.base.schemas import ErrorResponse, INTERNAL_ERR
from app.logging.dependencies import log


class ClientError(Exception):
    message: str
    error_code: str
    status_code: int
    headers: dict[str, str] | None = None

    def __init__(
        self,
        *,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        if message is not None:
            self.message = message
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code
        if headers is not None:
            self.headers = headers
        # make exception serializable
        super().__init__(self.message, self.error_code, self.status_code, self.headers)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(message="{self.message}", error_code={self.error_code}, status_code={self.status_code})'


class LongValidationError(RequestValidationError):
    pass


class ValidationError(LongValidationError):
    def __init__(self, msg: str) -> None:
        super().__init__([{"loc": "request", "msg": msg, "type": "invalid_request"}])


class Unauthorized(ClientError):
    message = "Unauthorized"
    error_code = "unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


def client_exception_handler(request: Request, ex: ClientError) -> JSONResponse:
    log.info('[BE] "%s %s" response: %s', request.method, request.url, repr(ex))
    return JSONResponse(
        status_code=ex.status_code,
        content=ErrorResponse(
            msg=ex.message,
            type=ex.error_code,
        ).model_dump(mode="json"),
        headers=ex.headers,
    )


def unhandled_exception_handler(request: Request, ex: Exception) -> JSONResponse:
    log.exception(f'"{request.method} {request.url}" failed: {repr(ex)}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=INTERNAL_ERR.model_dump(mode="json"),
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ClientError, client_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
