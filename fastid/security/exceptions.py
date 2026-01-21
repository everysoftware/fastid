from fastid.api.exceptions import ClientError


class JWTError(ClientError):
    pass


class TokenError(JWTError):
    pass


class InvalidTokenTypeError(JWTError):
    pass
