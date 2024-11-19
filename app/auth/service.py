from app.auth.exceptions import (
    UserNotFound,
    UserAlreadyExists,
)
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.schemas import (
    UserUpdate,
    UserCreate,
)
from app.authlib.dependencies import token_backend
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

    async def get_one(self, user_id: UUID) -> User:
        user = await self.get(user_id)
        if user is None:
            raise UserNotFound()
        return user

    async def get_userinfo(self, token: str) -> User:
        payload = token_backend.validate_at(token)
        return await self.get_one(UUID(payload.sub))

    async def get(self, user_id: UUID) -> User | None:
        return await self.uow.users.get(user_id)

    async def update(
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

    async def grant_superuser(self, user: User) -> User:
        user.grant_superuser()
        await self.uow.commit()
        return user

    async def revoke_superuser(self, user: User) -> User:
        user.revoke_superuser()
        await self.uow.commit()
        return user
