from app.apps.exceptions import AppNotFound
from app.apps.models import App
from app.apps.repositories import IsActiveApp
from app.apps.schemas import AppCreate
from app.base.service import UseCase
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep


class AppUseCases(UseCase):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache

    async def register(self, dto: AppCreate) -> App:
        app = App.from_dto(dto)
        return await self.uow.apps.add(app)

    async def get(self, client_id: str) -> App | None:
        return await self.uow.apps.find(IsActiveApp(client_id))

    async def get_one(self, client_id: str) -> App:
        app = await self.get(client_id)
        if app is None:
            raise AppNotFound()
        return app
