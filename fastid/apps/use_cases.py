from fastid.apps.exceptions import AppNotFoundError
from fastid.apps.models import App
from fastid.apps.repositories import AppClientIDSpecification
from fastid.apps.schemas import AppCreate, AppUpdate
from fastid.cache.dependencies import CacheDep
from fastid.core.use_cases import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.utils import UUIDv7


class AppUseCases(UseCase):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache

    async def register(self, dto: AppCreate) -> App:
        app = App.from_dto(dto)
        await self.uow.apps.add(app)
        await self.uow.commit()
        return app

    async def get(self, app_id: UUIDv7) -> App:
        try:
            return await self.uow.apps.get(app_id)
        except NoResultFoundError as e:
            raise AppNotFoundError from e

    async def get_by_client_id(self, client_id: str) -> App:
        try:
            return await self.uow.apps.find(AppClientIDSpecification(client_id))
        except NoResultFoundError as e:
            raise AppNotFoundError from e

    async def update(self, app: App, app_update: AppUpdate) -> App:
        app.merge_model(app_update)
        await self.uow.commit()
        return app

    async def delete(self, app: App) -> App:
        app = await self.uow.apps.delete(app)
        await self.uow.commit()
        return app
