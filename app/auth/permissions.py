from typing import Annotated

from fastapi import Depends

from app.auth.backend import verify_token_transport, token_backend
from app.auth.dependencies import UserDep
from app.auth.exceptions import NoPermission
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
        verify_token: Annotated[str | None, Depends(verify_token_transport)],
    ) -> User:
        if self.superuser is not None and user.is_superuser != self.superuser:
            raise NoPermission()
        if (
            self.email_verified is not None
            and user.is_verified != self.email_verified
        ):
            raise NoPermission()
        if self.active is not None and user.is_active != self.active:
            raise NoPermission()
        if self.action_verified and (
            verify_token is None
            or not self.token_backend.validate_custom("verify", verify_token)
        ):
            raise NoPermission()
        return user
