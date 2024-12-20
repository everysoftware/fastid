from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.base.repository import IRepository
from app.base.types import UUID
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpecification
from app.oauth.models import OAuthAccount


class IOAuthAccountRepository(IRepository[OAuthAccount], ABC):
    pass


class OAuthAccountRepository(
    IOAuthAccountRepository, AlchemyRepository[OAuthAccount]
):
    model_type = OAuthAccount


class IsAccountBelongToUser(AlchemySpecification):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(OAuthAccount.user_id == self.user_id)


class IsAccountConnected(AlchemySpecification):
    def __init__(self, provider: str, account_id: str) -> None:
        self.account_id = account_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccount.provider == self.provider,
            OAuthAccount.account_id == self.account_id,
        )


class IsAccountExists(AlchemySpecification):
    def __init__(self, user_id: UUID, provider: str) -> None:
        self.user_id = user_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccount.user_id == self.user_id,
            OAuthAccount.provider == self.provider,
        )
