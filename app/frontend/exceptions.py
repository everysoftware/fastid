from fastapi import Request, status, FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.exceptions import ClientError, Unauthorized
from app.base.schemas import ErrorResponse, INTERNAL_ERR
from app.main import logging

logger = logging.get_logger(__name__)


def unauthorized_handler(request: Request, ex: Unauthorized) -> Response:
    logger.info(
        '[FE] "%s %s" response: %s', request.method, request.url, repr(ex)
    )
    return RedirectResponse(url="/login")


def client_exception_handler(
    request: Request, ex: ClientError
) -> JSONResponse:
    logger.info(
        '[FE] "%s %s" response: %s', request.method, request.url, repr(ex)
    )
    return JSONResponse(
        status_code=ex.status_code,
        content=ErrorResponse(
            msg=ex.message,
            code=ex.error_code,
        ).model_dump(mode="json"),
        headers=ex.headers,
    )


def unhandled_exception_handler(
    request: Request, ex: Exception
) -> JSONResponse:
    logger.exception(f'"{request.method} {request.url}" failed: {repr(ex)}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=INTERNAL_ERR.model_dump(mode="json"),
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Unauthorized, unauthorized_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ClientError, client_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
