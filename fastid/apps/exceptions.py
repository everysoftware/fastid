from starlette import status

from fastid.api.exceptions import ClientError, UnauthorizedError


class AppNotFoundError(ClientError):
    message = "App with this client_id not found"
    error_code = "app_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class InvalidRedirectURIError(ClientError):
    message = "Invalid redirect URI"
    error_code = "invalid_redirect_uri"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidClientCredentialsError(UnauthorizedError):
    message = "Invalid client credentials"
    error_code = "invalid_client_credentials"


class InvalidAuthorizationCodeError(UnauthorizedError):
    message = "Invalid code"
    error_code = "invalid_code"
