from app.auth.dependencies import AuthDep
from app.auth.exceptions import NoPermission
from app.auth.models import User
from app.authlib.dependencies import UserDep


class Requires:
    def __init__(
        self,
        is_superuser: bool | None = None,
        is_oauth: bool | None = None,
        is_verified: bool | None = None,
        is_active: bool | None = None,
    ):
        self.is_superuser = is_superuser
        self.is_oauth = is_oauth
        self.is_verified = is_verified
        self.is_active = is_active

    async def __call__(
        self,
        users: AuthDep,
        user: UserDep,
    ) -> User:
        if (
            self.is_superuser is not None
            and user.is_superuser != self.is_superuser
        ):
            raise NoPermission()
        if self.is_oauth is not None and user.is_oauth != self.is_oauth:
            raise NoPermission()
        if (
            self.is_verified is not None
            and user.is_verified != self.is_verified
        ):
            raise NoPermission()
        if self.is_active is not None and user.is_active != self.is_active:
            raise NoPermission()
        return user
