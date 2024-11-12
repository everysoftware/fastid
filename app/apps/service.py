from app.apps.exceptions import ClientNotFound
from app.apps.repositories import IsAppExists
from app.apps.schemas import App, AppCreate
from app.db.dependencies import UOWDep
from app.domain.service import BaseUseCase


class AppUseCases(BaseUseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: AppCreate) -> App:
        item = App.from_model(dto)
        return await self.uow.apps.add(item)

    async def get_by_client_id(self, client_id: str) -> App | None:
        return await self.uow.apps.find(IsAppExists(client_id))

    async def get_one(self, client_id: str) -> App:
        item = await self.get_by_client_id(client_id)
        if item is None:
            raise ClientNotFound()
        return item
