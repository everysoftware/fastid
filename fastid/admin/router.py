from typing import Annotated, Any

from fastapi import APIRouter, Depends

from fastid.auth.dependencies import user_dep
from fastid.auth.models import User
from fastid.auth.permissions import Requires
from fastid.auth.schemas import UserDTO, UserUpdate
from fastid.database.schemas import LimitOffset, PageDTO, Sorting
from fastid.profile.dependencies import ProfilesDep, get_user_by_id

router = APIRouter(
    tags=["Admin"],
    dependencies=[user_dep, Depends(Requires(superuser=True))],
)


@router.get("/users/{user_id}")
def get_by_id(user: Annotated[UserDTO, Depends(get_user_by_id)]) -> UserDTO:
    return user


@router.patch("/users/{user_id}", response_model=UserDTO)
async def update_by_id(
    service: ProfilesDep,
    user: Annotated[User, Depends(get_user_by_id)],
    update: UserUpdate,
) -> Any:
    return await service.update_profile(user, update)


@router.delete("/users/{user_id}", response_model=UserDTO)
async def delete_by_id(service: ProfilesDep, user: Annotated[User, Depends(get_user_by_id)]) -> Any:
    return await service.delete_account(user)


@router.get("/users/", response_model=PageDTO[UserDTO])
async def get_many(
    service: ProfilesDep,
    pagination: Annotated[LimitOffset, Depends()],
    sorting: Annotated[Sorting, Depends()],
) -> Any:
    return await service.get_many(pagination, sorting)


@router.post("/users/{user_id}/grant", response_model=UserDTO)
async def grant(
    service: ProfilesDep,
    user: Annotated[User, Depends(get_user_by_id)],
) -> Any:
    return await service.grant_superuser(user)


@router.post("/users/{user_id}/revoke", response_model=UserDTO)
async def revoke(
    service: ProfilesDep,
    user: Annotated[User, Depends(get_user_by_id)],
) -> Any:
    return await service.revoke_superuser(user)
