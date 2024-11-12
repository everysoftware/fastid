from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.apps.models import AppOrm
from app.apps.schemas import App
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpec
from app.domain.repository import IRepository


class IAppRepository(IRepository[App], ABC):
    pass


class AppRepository(IAppRepository, AlchemyRepository[App]):
    model_type = App
    entity_type = AppOrm


class IsAppExists(AlchemySpec):
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(AppOrm.client_id == self.client_id)
