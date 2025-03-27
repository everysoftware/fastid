from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.exceptions import ClientError, UnauthorizedError
from app.base.schemas import INTERNAL_ERR, ErrorResponse
from app.logging.dependencies import log


class AuthorizedError(ClientError):
    status_code = status.HTTP_307_TEMPORARY_REDIRECT
    error_code = "authorized"
    message = "Already authorized"


def unauthorized_handler(request: Request, ex: UnauthorizedError) -> Response:
    log.info('[FE] "%s %s" response: %s', request.method, request.url, repr(ex))
    return RedirectResponse(url="/login")


def authorized_handler(request: Request, ex: AuthorizedError) -> Response:
    log.info('[FE] "%s %s" response: %s', request.method, request.url, repr(ex))
    return RedirectResponse(url="/profile")


def client_exception_handler(request: Request, ex: ClientError) -> JSONResponse:
    log.info('[FE] "%s %s" response: %s', request.method, request.url, repr(ex))
    return JSONResponse(
        status_code=ex.status_code,
        content=ErrorResponse(
            msg=ex.message,
            type=ex.error_code,
        ).model_dump(mode="json"),
        headers=ex.headers,
    )


def unhandled_exception_handler(request: Request, ex: Exception) -> JSONResponse:
    log.exception(f'[FE] "{request.method} {request.url}" failed: {ex!r}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=INTERNAL_ERR.model_dump(mode="json"),
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AuthorizedError, unauthorized_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UnauthorizedError, unauthorized_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ClientError, client_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
