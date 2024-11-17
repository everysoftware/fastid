from starlette import status

from app.api.exceptions import ClientError, Unauthorized


class NotSupportedGrant(Unauthorized):
    message = "Not supported grant type"
    error_code = "not_supported_grant"


class NoPermission(ClientError):
    message = "You don't have permission to do this"
    error_code = "no_permission"
    status_code = status.HTTP_403_FORBIDDEN


class UserAlreadyExists(ClientError):
    message = "User with this email already exists"
    error_code = "user_already_exists"
    status_code = status.HTTP_400_BAD_REQUEST


class UserEmailNotFound(ClientError):
    message = "User with this email not found"
    error_code = "user_email_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class UserNotFound(ClientError):
    message = "User with this id not found"
    error_code = "user_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class WrongPassword(Unauthorized):
    message = "Wrong password"
    error_code = "wrong_password"
