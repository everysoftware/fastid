from typing import Any

from fastid.auth.models import User
from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification


class UserRepository(SQLAlchemyRepository[User]):
    model_type = User


class UserEmailSpecification(Specification):
    def __init__(self, email: str) -> None:
        self.email = email

    def apply(self, stmt: Any) -> Any:
        return stmt.where(User.email == self.email, User.is_active.is_(True))
