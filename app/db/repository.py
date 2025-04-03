from abc import ABC
from collections.abc import Sequence
from typing import Any, ClassVar, TypeVar, cast

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.datatypes import UUIDv7
from app.base.models import Entity
from app.base.pagination import LimitOffset, Page, Pagination
from app.base.repository import IRepository
from app.base.sorting import Sorting
from app.base.specification import Specification
from app.db.exceptions import NoResultFoundError

T = TypeVar("T", bound=Entity)
S = TypeVar("S", bound=Select[Any])


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

    async def get(self, ident: UUIDv7) -> T | None:
        model = await self.session.get(self.model_type, ident)
        if model is None:
            return None
        return cast(T, model)

    async def get_one(self, ident: UUIDv7) -> T:
        model = await self.get(ident)
        if model is None:
            raise NoResultFoundError
        return model

    async def find(self, criteria: Specification) -> T | None:
        stmt = self._apply_params(
            self._select(),
            criteria=criteria,
            pagination=LimitOffset(limit=1),
        )
        result = await self.session.scalars(stmt)
        return result.first()

    async def find_one(self, criteria: Specification) -> T:
        model = await self.find(criteria)
        if model is None:
            raise NoResultFoundError
        return model

    async def remove(self, model: T) -> T:
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
