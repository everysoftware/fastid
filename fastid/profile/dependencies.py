from typing import Annotated

from fastapi import Depends

from fastid.auth.models import User
from fastid.database.utils import UUIDv7
from fastid.profile.use_cases import ProfileUseCases

ProfilesDep = Annotated[ProfileUseCases, Depends()]


async def get_user_by_id(service: ProfilesDep, user_id: UUIDv7) -> User:
    return await service.get(user_id)
