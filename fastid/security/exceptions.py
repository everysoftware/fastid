class JWTError(Exception):
    pass


class TokenError(JWTError):
    pass


class InvalidTokenTypeError(JWTError):
    pass
