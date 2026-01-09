from starlette import status

from fastid.api.exceptions import ClientError


class WrongCodeError(ClientError):
    message = "Wrong code"
    error_code = "wrong_code"
    status_code = status.HTTP_400_BAD_REQUEST


class TemplateNotFoundError(ClientError):
    message = "Template with this name does not exist"
    error_code = "template_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class NoEmailError(ClientError):
    message = "User with this id does not have any active email"
    error_code = "no_email"
    status_code = status.HTTP_400_BAD_REQUEST


class NoTelegramIDError(ClientError):
    message = "User with this id does not have any active telegram id"
    error_code = "no_telegram_id"
    status_code = status.HTTP_400_BAD_REQUEST
