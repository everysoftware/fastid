from starlette import status

from app.runner.exceptions import ClientError


class WrongCode(ClientError):
    message = "Wrong code"
    error_code = "wrong_code"
    status_code = status.HTTP_400_BAD_REQUEST
