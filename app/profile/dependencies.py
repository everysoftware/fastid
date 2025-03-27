from typing import Annotated

from fastapi import Depends

from app.auth.models import User
from app.base.types import UUIDv7
from app.profile.service import ProfileUseCases

ProfilesDep = Annotated[ProfileUseCases, Depends()]


async def get_user_by_id(service: ProfilesDep, user_id: UUIDv7) -> User:
    return await service.get_one(user_id)
