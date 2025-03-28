from starlette import status

from app.api.exceptions import ClientError, UnauthorizedError


class AppNotFoundError(ClientError):
    message = "App with this client_id not found"
    error_code = "app_not_found"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidRedirectURIError(ClientError):
    message = "Invalid redirect URI"
    error_code = "invalid_redirect_uri"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidClientCredentialsError(ClientError):
    message = "Invalid client credentials"
    error_code = "invalid_client_credentials"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidAuthorizationCodeError(UnauthorizedError):
    message = "Invalid code"
    error_code = "invalid_code"
    status_code = status.HTTP_400_BAD_REQUEST
