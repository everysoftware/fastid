from starlette import status

from app.api.exceptions import ClientError


class AppNotFound(ClientError):
    message = "App with this id not found"
    error_code = "app_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class InvalidRedirectURI(ClientError):
    message = "Invalid redirect URI"
    error_code = "invalid_redirect_uri"
    status_code = status.HTTP_404_NOT_FOUND
