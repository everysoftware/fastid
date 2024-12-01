from typing import Self, Any

from app.auth.exceptions import UserAlreadyExists
from app.auth.models import User
from app.auth.repositories import ActiveUserSpecification
from app.auth.schemas import UserCreate
from app.db.connection import session_factory
from app.db.uow import AlchemyUOW


class CLIUseCases:
    def __init__(self) -> None:
        self.uow = AlchemyUOW(session_factory)

    async def register_user(
        self,
        dto: UserCreate,
        is_admin: bool = False,
    ) -> None:
        user = await self.uow.users.find(ActiveUserSpecification(dto.email))
        if user:
            raise UserAlreadyExists()
        user = User(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
        )
        user.set_password(dto.password)
        if is_admin:
            user.grant_superuser()
        user.verify()
        await self.uow.users.add(user)

    async def __aenter__(self) -> Self:
        await self.uow.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: type[Exception], exc_val: Exception, exc_tb: Any
    ) -> None:
        await self.uow.__aexit__(exc_type, exc_val, exc_tb)
