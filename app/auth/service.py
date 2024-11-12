from typing import assert_never

from app.auth.exceptions import UserEmailNotFound, UserNotFound, WrongPassword
from app.auth.repositories import IsActiveUser
from app.auth.schemas import (
    UserUpdate,
    Role,
    UserCreate,
    User,
)
from app.authlib.schemas import OAuth2TokenRequest
from app.db.dependencies import UOWDep
from app.domain.pagination import Page, Pagination
from app.domain.sorting import Sorting
from app.domain.types import UUID
from app.domain.service import BaseUseCase


class AuthUseCases(BaseUseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: UserCreate) -> User:
        user = User.from_model(dto)
        user.hash_password()
        return await self.uow.users.add(user)

    async def get_by_email(self, email: str) -> User | None:
        return await self.uow.users.find(IsActiveUser(email))

    async def get_one_by_email(self, email: str) -> User:
        user = await self.get_by_email(email)
        if not user:
            raise UserEmailNotFound()
        return user

    async def get(self, user_id: UUID) -> User | None:
        return await self.uow.users.get(user_id)

    async def get_one(self, user_id: UUID) -> User:
        user = await self.get(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def update(
        self,
        user: User,
        dto: UserUpdate,
    ) -> User:
        user.merge_model(dto)
        return await self.uow.users.update(user)

    async def delete(self, user: User) -> User:
        return await self.uow.users.remove(user)

    async def authenticate(self, form: OAuth2TokenRequest) -> User:
        assert form.username is not None and form.password is not None
        user = await self.get_one_by_email(form.username)
        if not user.verify_password(form.password):
            raise WrongPassword()
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
        return await self.uow.users.add(user)
