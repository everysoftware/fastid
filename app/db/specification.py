from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Select

from app.base.specification import ISpecification


class AlchemySpec(ISpecification, ABC):
    @abstractmethod
    def apply[T: Select[Any]](self, stmt: T) -> T: ...
