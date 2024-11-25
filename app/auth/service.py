from app.auth.exceptions import (
    UserIDNotFound,
    UserAlreadyExists,
)
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.schemas import (
    UserUpdate,
    UserCreate,
    UserChangeEmail,
    UserChangePassword,
)
from app.authlib.dependencies import token_backend
from app.base.pagination import Pagination, Page
from app.base.service import UseCase
from app.base.sorting import Sorting
from app.base.types import UUID
from app.db.dependencies import UOWDep
from app.notifylib.dependencies import NotifierDep
from app.notifylib.templates import (
    WelcomeNotification,
)


class UserManagementUseCases(UseCase):
    def __init__(self, uow: UOWDep, notifier: NotifierDep) -> None:
        self.uow = uow
        self.notifier = notifier

    async def register(self, dto: UserCreate) -> User:
        user = await self.uow.users.find(IsActiveUser(dto.email))
        if user is not None:
            raise UserAlreadyExists()
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.notifier.push(WelcomeNotification(user=user))
        await self.uow.commit()
        return user

    async def get_one(self, user_id: UUID) -> User:
        user = await self.get(user_id)
        if user is None:
            raise UserIDNotFound()
        return user

    async def get_userinfo(self, token: str) -> User:
        payload = token_backend.validate_at(token)
        return await self.get_one(UUID(payload.sub))

    async def get(self, user_id: UUID) -> User | None:
        return await self.uow.users.get(user_id)

    async def update_profile(
        self,
        user: User,
        dto: UserUpdate,
    ) -> User:
        user.merge_model(dto)
        await self.uow.commit()
        return user

    async def change_email(self, user: User, dto: UserChangeEmail) -> User:
        check_user = await self.uow.users.find(IsActiveUser(dto.new_email))
        if check_user is not None:
            raise UserAlreadyExists()
        user.change_email(dto.new_email)
        await self.uow.commit()
        return user

    async def change_password(
        self, user: User, dto: UserChangePassword
    ) -> User:
        user.change_password(dto.password)
        await self.uow.commit()
        return user

    async def delete_account(self, user: User) -> User:
        await self.uow.users.remove(user)
        await self.uow.commit()
        return user

    async def get_many(
        self, pagination: Pagination, sorting: Sorting
    ) -> Page[User]:
        return await self.uow.users.get_many(
            pagination=pagination, sorting=sorting
        )

    async def grant_superuser(self, user: User) -> User:
        user.grant_superuser()
        await self.uow.commit()
        return user

    async def revoke_superuser(self, user: User) -> User:
        user.revoke_superuser()
        await self.uow.commit()
        return user
