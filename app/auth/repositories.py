from typing import Any

from app.auth.models import User
from app.base.specification import Specification
from app.db.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model_type = User


class UserEmailSpecification(Specification):
    def __init__(self, email: str) -> None:
        self.email = email

    def apply(self, stmt: Any) -> Any:
        return stmt.where(User.email == self.email, User.is_active.is_(True))
