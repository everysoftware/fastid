from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.auth.models import UserOrm
from app.auth.schemas import User
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpec
from app.domain.repository import IRepository


class IUserRepository(IRepository[User], ABC):
    pass


class UserRepository(IUserRepository, AlchemyRepository[User]):
    model_type = User
    entity_type = UserOrm


class IsActiveUser(AlchemySpec):
    def __init__(self, email: str) -> None:
        self.email = email

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            UserOrm.email == self.email, UserOrm.is_active.is_(True)
        )
