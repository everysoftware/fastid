from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.base.models import Entity
from app.base.pagination import Pagination, LimitOffset, Page
from app.base.sorting import Sorting
from app.base.specification import ISpecification
from app.base.types import UUID

T = TypeVar("T", bound=Entity)


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def add(self, model: T) -> T: ...

    @abstractmethod
    async def get(self, id: UUID) -> T | None: ...

    @abstractmethod
    async def get_one(self, id: UUID) -> T: ...

    @abstractmethod
    async def find(self, criteria: ISpecification) -> T | None: ...

    @abstractmethod
    async def find_one(self, criteria: ISpecification) -> T: ...

    @abstractmethod
    async def remove(self, model: T) -> T: ...

    @abstractmethod
    async def get_many(
        self,
        criteria: ISpecification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting = Sorting(),
    ) -> Page[T]: ...
