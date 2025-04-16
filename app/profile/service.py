from app.auth.exceptions import (
    UserAlreadyExistsError,
    UserIDNotFoundError,
)
from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.auth.schemas import (
    UserChangeEmail,
    UserChangePassword,
    UserUpdate,
)
from app.base.datatypes import UUIDv7
from app.base.pagination import Page, Pagination
from app.base.service import UseCase
from app.base.sorting import Sorting
from app.db.dependencies import UOWDep


class ProfileUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def get(self, user_id: UUIDv7) -> User | None:
        return await self.uow.users.get(user_id)

    async def get_one(self, user_id: UUIDv7) -> User:
        user = await self.get(user_id)
        if user is None:
            raise UserIDNotFoundError
        return user

    async def update_profile(
        self,
        user: User,
        dto: UserUpdate,
    ) -> User:
        user.merge_model(dto)
        await self.uow.commit()
        return user

    async def change_email(self, user: User, dto: UserChangeEmail) -> User:
        check_user = await self.uow.users.find(UserEmailSpecification(dto.new_email))
        if check_user is not None:
            raise UserAlreadyExistsError
        user.change_email(dto.new_email)
        await self.uow.commit()
        return user

    async def change_password(self, user: User, dto: UserChangePassword) -> User:
        user.set_password(dto.password)
        await self.uow.commit()
        return user

    async def delete_account(self, user: User) -> User:
        await self.uow.users.delete(user)
        await self.uow.commit()
        return user

    async def get_many(self, pagination: Pagination, sorting: Sorting) -> Page[User]:
        return await self.uow.users.get_many(pagination=pagination, sorting=sorting)

    async def grant_superuser(self, user: User) -> User:
        user.grant_superuser()
        await self.uow.commit()
        return user

    async def revoke_superuser(self, user: User) -> User:
        user.revoke_superuser()
        await self.uow.commit()
        return user
