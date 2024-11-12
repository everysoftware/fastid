from starlette import status

from app.runner.exceptions import ClientError


class OAuth2Error(Exception):
    pass


class ProviderNotAllowed(ClientError):
    message = "This OAuth provider is not allowed"
    error_code = "oauth_not_allowed"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
