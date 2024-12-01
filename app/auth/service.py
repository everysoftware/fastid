from app.auth.backend import token_backend
from app.auth.exceptions import UserIDNotFound, UserAlreadyExists
from app.auth.models import User
from app.auth.repositories import ActiveUserSpecification
from app.auth.schemas import UserCreate
from app.base.service import UseCase
from app.base.types import UUID
from app.db.dependencies import UOWDep


class AuthUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: UserCreate) -> User:
        user = await self.uow.users.find(ActiveUserSpecification(dto.email))
        if user is not None:
            raise UserAlreadyExists()
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.uow.commit()
        return user

    async def get_userinfo(self, token: str) -> User:
        payload = token_backend.validate_at(token)
        user = await self.uow.users.get(UUID(payload.sub))
        if user is None:
            raise UserIDNotFound()
        return user
