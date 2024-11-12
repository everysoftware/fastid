from starlette import status

from app.runner.exceptions import ClientError


class ClientNotFound(ClientError):
    message = "Client with this id not found"
    error_code = "client_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class InvalidRedirectURI(ClientError):
    message = "Invalid redirect URI"
    error_code = "invalid_redirect_uri"
    status_code = status.HTTP_404_NOT_FOUND
