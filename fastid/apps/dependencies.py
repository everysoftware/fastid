from typing import Annotated

from fastapi import Depends

from fastid.apps.models import App
from fastid.apps.use_cases import AppUseCases
from fastid.database.utils import UUIDv7

AppsDep = Annotated[AppUseCases, Depends()]


async def get_app(service: AppsDep, app_id: UUIDv7) -> App:
    return await service.get(app_id)
