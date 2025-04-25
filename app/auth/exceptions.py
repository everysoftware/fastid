from starlette import status

from app.api.exceptions import ClientError, UnauthorizedError


class NotSupportedGrantError(UnauthorizedError):
    message = "Grant type must be 'password', 'authorization_code' or 'refresh_token'"
    error_code = "not_supported_grant"
    status_code = status.HTTP_400_BAD_REQUEST


class NotSupportedResponseTypeError(UnauthorizedError):
    message = "Response type must be 'code'"
    error_code = "not_supported_response_type"
    status_code = status.HTTP_400_BAD_REQUEST


class NoPermissionError(ClientError):
    message = "You don't have permission to do this"
    error_code = "no_permission"
    status_code = status.HTTP_403_FORBIDDEN


class UserAlreadyExistsError(ClientError):
    message = "User with this email already exists"
    error_code = "user_already_exists"
    status_code = status.HTTP_400_BAD_REQUEST


class UserIDNotFoundError(ClientError):
    message = "User with this id not found"
    error_code = "user_not_found"
    status_code = status.HTTP_400_BAD_REQUEST


class EmailNotFoundError(UnauthorizedError):
    message = "User with this email not found"
    error_code = "user_email_not_found"


class WrongPasswordError(UnauthorizedError):
    message = "Wrong password"
    error_code = "wrong_password"


class NoTokenProvidedError(UnauthorizedError):
    message = "No access token provided"
    error_code = "no_token_provided"


class InvalidTokenError(UnauthorizedError):
    message = "Invalid token"
    error_code = "invalid_token"


class InvalidTokenTypeError(UnauthorizedError):
    error_code = "invalid_token_type"
