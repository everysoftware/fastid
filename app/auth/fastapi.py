from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2AuthorizationCodeBearer,
)

auth_flows = [
    OAuth2PasswordBearer(
        tokenUrl="auth/token", scheme_name="Password", auto_error=False
    ),
    OAuth2AuthorizationCodeBearer(
        authorizationUrl="oauth/login/google",
        tokenUrl="oauth/token/google",
        refreshUrl="auth/token",
        scheme_name="GoogleOAuth",
        auto_error=False,
    ),
    OAuth2AuthorizationCodeBearer(
        authorizationUrl="oauth/login/yandex",
        tokenUrl="oauth/token/yandex",
        refreshUrl="auth/token",
        scheme_name="YandexOAuth",
        auto_error=False,
    ),
]
