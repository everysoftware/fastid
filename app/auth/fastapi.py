from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2AuthorizationCodeBearer,
)

auth_flows = [
    OAuth2PasswordBearer(
        tokenUrl="auth/token", scheme_name="Password", auto_error=False
    ),
    OAuth2AuthorizationCodeBearer(
        authorizationUrl="oauth/google/login",
        tokenUrl="oauth/google/token",
        refreshUrl="auth/token",
        scheme_name="GoogleOAuth",
        auto_error=False,
    ),
    OAuth2AuthorizationCodeBearer(
        authorizationUrl="oauth/yandex/login",
        tokenUrl="oauth/yandex/token",
        refreshUrl="auth/token",
        scheme_name="YandexOAuth",
        auto_error=False,
    ),
]
