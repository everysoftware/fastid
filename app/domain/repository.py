from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.domain.pagination import Pagination, LimitOffset, Page
from app.domain.schemas import DomainModel
from app.domain.sorting import Sorting
from app.domain.specification import ISpecification
from app.domain.types import UUID

T = TypeVar("T", bound=DomainModel)


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
    async def update(self, model: T) -> T: ...

    @abstractmethod
    async def remove(self, model: T) -> T: ...

    @abstractmethod
    async def get_many(
        self,
        criteria: ISpecification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting = Sorting(),
    ) -> Page[T]: ...
