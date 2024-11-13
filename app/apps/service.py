from app.apps.exceptions import AppNotFound
from app.apps.models import App
from app.apps.repositories import IsAppExists
from app.apps.schemas import AppCreate
from app.base.service import UseCases
from app.db.dependencies import UOWDep


class AppUseCases(UseCases):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: AppCreate) -> App:
        app = App.from_dto(dto)
        return await self.uow.apps.add(app)

    async def get(self, client_id: str) -> App | None:
        return await self.uow.apps.find(IsAppExists(client_id))

    async def get_one(self, client_id: str) -> App:
        app = await self.get(client_id)
        if app is None:
            raise AppNotFound()
        return app
