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


class InvalidContactTypeError(ClientError):
    message = "Invalid contact type"
    error_code = "invalid_contact_type"
    status_code = status.HTTP_400_BAD_REQUEST


class MethodDisabledError(ClientError):
    message = "Notification method is disabled. Enable it in settings to send notifications"
    error_code = "notification_method_disabled"
    status_code = status.HTTP_400_BAD_REQUEST


class NotificationDisabledError(ClientError):
    message = "Notifications are disabled. Enable at least one notification method to send notifications"
    error_code = "notification_disabled"
    status_code = status.HTTP_400_BAD_REQUEST
