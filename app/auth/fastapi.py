from fastapi.security import (
    OAuth2PasswordBearer,
)

auth_flows = [
    OAuth2PasswordBearer(
        tokenUrl="auth/token", scheme_name="Password", auto_error=False
    ),
]
