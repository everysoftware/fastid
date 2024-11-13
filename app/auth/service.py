from typing import assert_never

from app.auth.exceptions import UserNotFound, UserAlreadyExists
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.schemas import (
    UserUpdate,
    Role,
    UserCreate,
)
from app.authlib.schemas import OAuth2TokenRequest
from app.base.pagination import Pagination, Page
from app.base.service import UseCases
from app.base.sorting import Sorting
from app.base.types import UUID
from app.db.dependencies import UOWDep


class AuthUseCases(UseCases):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: UserCreate) -> User:
        user = await self.uow.users.find(IsActiveUser(dto.email))
        if user is not None:
            raise UserAlreadyExists()
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.uow.commit()
        return user

    async def authenticate(self, form: OAuth2TokenRequest) -> User:
        assert form.username is not None and form.password is not None
        user = await self.uow.users.find(IsActiveUser(form.username))
        if user is None:
            raise UserNotFound()
        user.verify_password(form.password)
        return user

    async def get(self, user_id: UUID) -> User | None:
        return await self.uow.users.get(user_id)

    async def get_one(self, user_id: UUID) -> User:
        user = await self.get(user_id)
        if user is None:
            raise UserNotFound()
        return user

    async def update_profile(
        self,
        user: User,
        dto: UserUpdate,
    ) -> User:
        user.merge_model(dto)
        await self.uow.commit()
        return user

    async def delete(self, user: User) -> User:
        await self.uow.users.remove(user)
        await self.uow.commit()
        return user

    async def get_many(
        self, pagination: Pagination, sorting: Sorting
    ) -> Page[User]:
        return await self.uow.users.get_many(
            pagination=pagination, sorting=sorting
        )

    async def grant(self, user: User, role: Role) -> User:
        match role:
            case Role.user:
                user.revoke_superuser()
            case Role.superuser:
                user.grant_superuser()
            case _:
                assert_never(role)
        await self.uow.commit()
        return user
