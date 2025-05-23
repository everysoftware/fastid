from fastid.auth.dependencies import UserDep
from fastid.auth.exceptions import NoPermissionError
from fastid.auth.models import User
from fastid.security.jwt import jwt_backend


class Requires:
    def __init__(
        self,
        *,
        superuser: bool | None = None,
        email_verified: bool | None = None,
        active: bool | None = None,
    ) -> None:
        self.superuser = superuser
        self.email_verified = email_verified
        self.active = active
        self.token_backend = jwt_backend

    async def __call__(
        self,
        user: UserDep,
    ) -> User:
        if self.superuser is not None and user.is_superuser != self.superuser:
            raise NoPermissionError
        if self.email_verified is not None and user.is_verified != self.email_verified:  # pragma: nocover
            raise NoPermissionError
        if self.active is not None and user.is_active != self.active:  # pragma: nocover
            raise NoPermissionError
        return user
