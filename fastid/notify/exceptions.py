from starlette import status

from fastid.api.exceptions import ClientError


class WrongCodeError(ClientError):
    message = "Wrong code"
    error_code = "wrong_code"
    status_code = status.HTTP_400_BAD_REQUEST
