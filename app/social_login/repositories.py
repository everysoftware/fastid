from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpec
from app.domain.repository import IRepository
from app.domain.types import UUID
from app.social_login.models import OAuthAccountOrm
from app.social_login.schemas import OAuthAccount


class IOAuthAccountRepository(IRepository[OAuthAccount], ABC):
    pass


class OAuthAccountRepository(
    IOAuthAccountRepository, AlchemyRepository[OAuthAccount]
):
    model_type = OAuthAccount
    entity_type = OAuthAccountOrm


class IsAccountBelongToUser(AlchemySpec):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(OAuthAccountOrm.user_id == self.user_id)


class IsAccountConnected(AlchemySpec):
    def __init__(self, provider: str, account_id: str) -> None:
        self.account_id = account_id
        self.provider = provider

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            OAuthAccountOrm.provider == self.provider,
            OAuthAccountOrm.account_id == self.account_id,
        )
