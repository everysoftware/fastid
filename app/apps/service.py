from app.apps.exceptions import AppNotFoundError
from app.apps.models import App
from app.apps.repositories import AppClientIDSpecification
from app.apps.schemas import AppCreate
from app.base.datatypes import UUIDv7
from app.base.service import UseCase
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep


class AppUseCases(UseCase):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache

    async def register(self, dto: AppCreate) -> App:
        app = App.from_dto(dto)
        await self.uow.apps.add(app)
        await self.uow.commit()
        return app

    async def get(self, app_id: UUIDv7) -> App | None:
        return await self.uow.apps.get(app_id)

    async def get_one(self, app_id: UUIDv7) -> App:
        app = await self.get(app_id)
        if app is None:
            raise AppNotFoundError
        return app

    async def get_by_client_id(self, client_id: str) -> App | None:
        return await self.uow.apps.find(AppClientIDSpecification(client_id))

    async def get_one_by_client_id(self, client_id: str) -> App:
        app = await self.get_by_client_id(client_id)
        if app is None:
            raise AppNotFoundError
        return app
