from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.base.models import Entity
from app.base.pagination import LimitOffset, Page, Pagination
from app.base.sorting import Sorting
from app.base.specification import Specification
from app.base.types import UUIDv7

T = TypeVar("T", bound=Entity)


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def add(self, model: T) -> T: ...

    @abstractmethod
    async def get(self, id: UUIDv7) -> T | None: ...

    @abstractmethod
    async def get_one(self, id: UUIDv7) -> T: ...

    @abstractmethod
    async def find(self, criteria: Specification) -> T | None: ...

    @abstractmethod
    async def find_one(self, criteria: Specification) -> T: ...

    @abstractmethod
    async def remove(self, model: T) -> T: ...

    @abstractmethod
    async def get_many(
        self,
        criteria: Specification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting = Sorting(),
    ) -> Page[T]: ...
