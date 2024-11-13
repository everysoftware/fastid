from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.base.repository import IRepository
from app.base.types import UUID
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpec
from app.social.models import OAuthAccount


class IOAuthAccountRepository(IRepository[OAuthAccount], ABC):
    pass


class OAuthAccountRepository(
    IOAuthAccountRepository, AlchemyRepository[OAuthAccount]
):
    model_type = OAuthAccount


class IsAccountBelongToUser(AlchemySpec):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(OAuthAccount.user_id == self.user_id)


class IsAccountConnected(AlchemySpec):
    def __init__(self, provider: str, account_id: str) -> None:
        self.account_id = account_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccount.provider == self.provider,
            OAuthAccount.account_id == self.account_id,
        )
