from typing import Any

from fastid.apps.models import App
from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification


class AppRepository(SQLAlchemyRepository[App]):
    model_type = App


class AppClientIDSpecification(Specification):
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def apply(self, stmt: Any) -> Any:
        return stmt.where(App.client_id == self.client_id, App.is_active.is_(True))
