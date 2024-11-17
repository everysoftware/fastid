from app.api.exceptions import Unauthorized


class NoTokenProvided(Unauthorized):
    message = "No access token provided"
    error_code = "no_token_provided"


class InvalidToken(Unauthorized):
    message = "Invalid token"
    error_code = "invalid_token"


class InvalidTokenType(Unauthorized):
    error_code = "invalid_token_type"
