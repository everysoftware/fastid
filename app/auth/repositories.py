from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.auth.models import User
from app.base.repository import IRepository
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpecification


class IUserRepository(IRepository[User], ABC):
    pass


class UserRepository(IUserRepository, AlchemyRepository[User]):
    model_type = User


class ActiveUserSpecification(AlchemySpecification):
    def __init__(self, email: str) -> None:
        self.email = email

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(User.email == self.email, User.is_active.is_(True))
