from abc import ABC
from typing import TypeVar, Any, ClassVar, Sequence, cast

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseEntityOrm
from app.db.exceptions import NoResultFound
from app.domain.pagination import Page, Pagination, LimitOffset
from app.domain.repository import IRepository
from app.domain.schemas import DomainModel
from app.domain.sorting import Sorting
from app.domain.specification import ISpecification
from app.domain.types import UUID

T = TypeVar("T", bound=DomainModel)
S = TypeVar("S", bound=Select[tuple[Any, ...]])


class AlchemyRepository(IRepository[T], ABC):
    model_type: ClassVar[type[DomainModel]]
    entity_type: ClassVar[type[BaseEntityOrm]]

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def add(self, model: T) -> T:
        entity = self.entity_type(**model.model_dump())
        self.session.add(entity)
        return model

    async def get(self, id: UUID) -> T | None:
        entity = await self.session.get(self.entity_type, id)
        if entity is None:
            return None
        return self._to_model(entity)

    async def get_one(self, id: UUID) -> T:
        model = await self.get(id)
        if model is None:
            raise NoResultFound()
        return model

    async def find(self, criteria: ISpecification) -> T | None:
        stmt = self._apply_params(
            self._select(),
            criteria=criteria,
            pagination=LimitOffset(limit=1),
        )
        result = await self.session.scalars(stmt)
        return self._to_model(result.first())

    async def find_one(self, criteria: ISpecification) -> T:
        model = await self.find(criteria)
        if model is None:
            raise NoResultFound()
        return model

    async def update(self, model: T) -> T:
        entity = self._to_entity(model)
        await self.session.merge(entity)
        return model

    async def remove(self, model: T) -> T:
        entity = await self.session.get_one(self.entity_type, model.id)
        await self.session.delete(entity)
        return model

    async def get_many(
        self,
        criteria: ISpecification | None = None,
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

    def _to_model(self, entity: Any | None) -> T | None:
        if entity is None:
            return None
        return cast(T, self.model_type.model_validate(entity))

    def _to_entity(self, model: T) -> Any:
        return self.entity_type(**model.model_dump())

    def _to_page(self, entities: Sequence[Any]) -> Page[T]:  # noqa
        return Page[T](items=entities)

    def _select(self) -> Select[tuple[Any]]:
        return select(self.entity_type)

    @staticmethod
    def _apply_criteria(stmt: S, criteria: ISpecification) -> S:
        return cast(S, criteria.apply(stmt))

    @staticmethod
    def _apply_pagination(stmt: S, pagination: Pagination) -> S:
        if isinstance(pagination, LimitOffset):
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)
        return stmt

    def _apply_sorting(self, stmt: S, sorting: Sorting) -> S:
        for entry in sorting.entries():
            attr = getattr(self.entity_type, entry.field)
            return stmt.order_by(
                attr.asc() if entry.order == "asc" else attr.desc()
            )
        return stmt

    def _apply_params(
        self,
        stmt: S,
        criteria: ISpecification | None = None,
        pagination: Pagination = LimitOffset(),
        sorting: Sorting | None = None,
    ) -> S:
        if criteria is not None:
            stmt = self._apply_criteria(stmt, criteria)
        stmt = self._apply_pagination(stmt, pagination)
        if sorting is not None:
            stmt = self._apply_sorting(stmt, sorting)
        return stmt
