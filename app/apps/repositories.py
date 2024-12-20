from abc import ABC
from typing import Any

from sqlalchemy import Select

from app.apps.models import App
from app.base.repository import IRepository
from app.db.repository import AlchemyRepository
from app.db.specification import AlchemySpecification


class IAppRepository(IRepository[App], ABC):
    pass


class AppRepository(IAppRepository, AlchemyRepository[App]):
    model_type = App


class IsActiveApp(AlchemySpecification):
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(
            App.client_id == self.client_id, App.is_active.is_(True)
        )


class IsActiveAppSlug(AlchemySpecification):
    def __init__(self, slug: str) -> None:
        self.slug = slug

    def apply[T: Select[Any]](self, stmt: T) -> T:
        return stmt.where(App.slug == self.slug, App.is_active.is_(True))
