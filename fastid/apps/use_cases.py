from fastid.apps.exceptions import AppNotFoundError
from fastid.apps.models import App
from fastid.apps.schemas import AppCreate, AppUpdate
from fastid.cache.dependencies import CacheDep
from fastid.core.base import UseCase
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

    async def update(self, app: App, app_update: AppUpdate) -> App:
        # Serialize DB mutations and refresh any identity changed concurrently.
        # Mutations never wait on a Redis fill while holding a DB connection.
        await self.uow.session.refresh(app, with_for_update=True)
        old_client_id = app.client_id
        app.merge_model(app_update)
        await self.uow.commit()
        for client_id in {old_client_id, app.client_id}:
            await self.cache.invalidate(f"apps:{client_id}")
        return app

    async def delete(self, app: App) -> App:
        await self.uow.session.refresh(app, with_for_update=True)
        client_id = app.client_id
        app = await self.uow.apps.delete(app)
        await self.uow.commit()
        await self.cache.invalidate(f"apps:{client_id}")
        return app
