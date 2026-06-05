class IntegrationError(Exception):
    pass


class TokenError(IntegrationError):
    pass


class DiscoveryError(IntegrationError):
    pass


class ClientError(IntegrationError):
    pass


class RedirectURIError(IntegrationError):
    pass


class AuthorizationError(IntegrationError):
    pass


class UserinfoError(IntegrationError):
    pass


class StateError(IntegrationError):
    pass


class InvalidTokenTypeError(IntegrationError):
    pass


class HashMismatchError(IntegrationError):
    pass


class ExpirationError(IntegrationError):
    pass
