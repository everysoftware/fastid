from typing import Any

from sqlalchemy import Select

from app.base.specification import Specification
from app.base.types import UUID
from app.db.repository import SQLAlchemyRepository
from app.oauth.models import OAuthAccount


class OAuthAccountRepository(SQLAlchemyRepository[OAuthAccount]):
    model_type = OAuthAccount


class UserAccountSpecification(Specification):
    def __init__(self, user_id: UUID, provider: str) -> None:
        self.user_id = user_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccount.user_id == self.user_id,
            OAuthAccount.provider == self.provider,
        )


class UserAccountPageSpecification(Specification):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(OAuthAccount.user_id == self.user_id)


class ProviderAccountSpecification(Specification):
    def __init__(self, provider: str, account_id: str) -> None:
        self.account_id = account_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccount.provider == self.provider,
            OAuthAccount.account_id == self.account_id,
        )
