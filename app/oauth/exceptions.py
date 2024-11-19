from starlette import status

from app.api.exceptions import ClientError


class OAuthAccountNotFound(ClientError):
    message = "OAuth account with this id not found"
    error_code = "oauth_account_not_found"
    status_code = status.HTTP_400_BAD_REQUEST


class OAuthAccountInUse(ClientError):
    message = "OAuth account is in use"
    error_code = "oauth_account_in_use"
    status_code = status.HTTP_400_BAD_REQUEST


class ProviderNotAllowed(ClientError):
    message = "This OAuth provider is not allowed"
    error_code = "provider_not_allowed"
    status_code = status.HTTP_400_BAD_REQUEST
