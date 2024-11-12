from starlette import status

from app.runner.exceptions import ClientError


class OAuthAccountNotFound(ClientError):
    message = "OAuth account with this id not found"
    error_code = "oauth_account_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class OAuthAlreadyConnected(ClientError):
    message = "OAuth account is in use"
    error_code = "oauth_already_associated"
    status_code = status.HTTP_400_BAD_REQUEST


class UserTelegramNotFound(ClientError):
    message = "User with this telegram id not found"
    error_code = "telegram_id_not_found"
    status_code = status.HTTP_400_BAD_REQUEST
