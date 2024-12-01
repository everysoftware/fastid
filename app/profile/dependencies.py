from typing import Annotated

from fastapi import Depends

from app.auth.models import User
from app.base.types import UUID
from app.profile.service import ProfileUseCases

ProfilesDep = Annotated[ProfileUseCases, Depends()]


async def get_user_by_id(service: ProfilesDep, user_id: UUID) -> User:
    return await service.get_one(user_id)
