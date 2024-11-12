from starlette import status

from app.runner.exceptions import ClientError, Unauthorized


class NoTokenProvided(Unauthorized):
    message = "No access token provided"
    error_code = "no_token_provided"


class InvalidToken(Unauthorized):
    message = "Invalid token"
    error_code = "invalid_token"


class InvalidTokenType(Unauthorized):
    error_code = "invalid_token_type"


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
