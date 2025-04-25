from typing import Annotated

from fastapi import Depends

from app.apps.models import App
from app.apps.service import AppUseCases
from app.base.datatypes import UUIDv7

AppsDep = Annotated[AppUseCases, Depends()]


async def get_app(service: AppsDep, app_id: UUIDv7) -> App:
    return await service.get(app_id)
