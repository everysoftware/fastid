from fastapi import Request

from app.auth.backend import token_backend, verify_token_transport
from app.auth.dependencies import UserDep
from app.auth.exceptions import NoPermissionError
from app.auth.models import User


class Requires:
    def __init__(
        self,
        *,
        superuser: bool | None = None,
        email_verified: bool | None = None,
        active: bool | None = None,
        action_verified: bool | None = None,
    ) -> None:
        self.superuser = superuser
        self.email_verified = email_verified
        self.active = active
        self.action_verified = action_verified
        self.token_backend = token_backend

    async def __call__(
        self,
        user: UserDep,
        request: Request,
    ) -> User:
        verify_token = verify_token_transport.get_token(request)
        if self.superuser is not None and user.is_superuser != self.superuser:
            raise NoPermissionError
        if self.email_verified is not None and user.is_verified != self.email_verified:
            raise NoPermissionError
        if self.active is not None and user.is_active != self.active:
            raise NoPermissionError
        if self.action_verified and (verify_token is None or not self.token_backend.validate("verify", verify_token)):
            raise NoPermissionError
        return user
