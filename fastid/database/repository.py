from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar, Generic, TypeVar, cast

from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from fastid.database.base import Entity
from fastid.database.exceptions import NoResultFoundError, NotSupportedPaginationError
from fastid.database.schemas import LimitOffset, Page, Pagination, Sorting
from fastid.database.specification import Specification
from fastid.database.utils import UUIDv7

T = TypeVar("T", bound=Entity)
S = TypeVar("S", bound=Select[Any])


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def add(self, model: T) -> T: ...

    @abstractmethod
    async def get(self, ident: UUIDv7) -> T: ...

    @abstractmethod
    async def find(self, criteria: Specification) -> T: ...

    @abstractmethod
    async def delete(self, model: T) -> T: ...

    @abstractmethod
    async def get_many(
        self,
        criteria: Specification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting = Sorting(),
    ) -> Page[T]: ...


class SQLAlchemyRepository(IRepository[T], ABC):
    model_type: ClassVar[type[Entity]]

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def add(self, model: T) -> T:
        self.session.add(model)
        return model

    async def get(self, ident: UUIDv7) -> T:
        try:
            model = await self.session.get_one(self.model_type, ident)
        except NoResultFound as e:
            raise NoResultFoundError from e
        return cast(T, model)

    async def find(self, criteria: Specification) -> T:
        stmt = self._apply_params(
            self._select(),
            criteria=criteria,
            pagination=LimitOffset(limit=1),
        )
        result = await self.session.scalars(stmt)
        try:
            model = result.one()
        except NoResultFound as e:
            raise NoResultFoundError from e
        return model

    async def delete(self, model: T) -> T:
        await self.session.delete(model)
        return model

    async def get_many(
        self,
        criteria: Specification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting | None = None,
    ) -> Page[T]:
        result = await self.session.scalars(
            self._apply_params(
                self._select(),
                criteria=criteria,
                sorting=sorting,
                pagination=pagination,
            )
        )
        return self._to_page(result.all())

    @staticmethod
    def _to_page(entities: Sequence[Any]) -> Page[T]:
        return Page(items=entities)

    def _select(self) -> Select[tuple[T]]:
        return select(self.model_type)

    @staticmethod
    def _apply_criteria(stmt: S, criteria: Specification) -> S:
        return cast(S, criteria.apply(stmt))

    @staticmethod
    def _apply_pagination(stmt: S, pagination: Pagination) -> S:
        if isinstance(pagination, LimitOffset):
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)
        else:
            raise NotSupportedPaginationError
        return stmt

    def _apply_sorting(self, stmt: S, sorting: Sorting) -> S:
        for entry in sorting.render(self.model_type):
            attr = getattr(self.model_type, entry.field)
            stmt = stmt.order_by(attr.asc() if entry.order == "asc" else attr.desc())
        return stmt

    def _apply_params(
        self,
        stmt: S,
        criteria: Specification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting | None = None,
    ) -> S:
        if criteria is not None:
            stmt = self._apply_criteria(stmt, criteria)
        stmt = self._apply_pagination(stmt, pagination)
        if sorting is not None:
            stmt = self._apply_sorting(stmt, sorting)
        return stmt
