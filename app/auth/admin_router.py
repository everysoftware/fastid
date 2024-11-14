from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_user_by_id, AuthDep, user_dep
from app.auth.models import User
from app.auth.permissions import Requires
from app.auth.schemas import UserDTO, UserUpdate
from app.base.pagination import LimitOffset, PageDTO
from app.base.sorting import Sorting

router = APIRouter(
    tags=["Admin"],
    dependencies=[user_dep, Depends(Requires(is_superuser=True))],
)


@router.get("/users/{user_id}")
def get_by_id(user: Annotated[UserDTO, Depends(get_user_by_id)]) -> UserDTO:
    return user


@router.patch("/users/{user_id}", response_model=UserDTO)
async def update_by_id(
    service: AuthDep,
    user: Annotated[User, Depends(get_user_by_id)],
    update: UserUpdate,
) -> Any:
    return await service.update(user, update)


@router.delete("/users/{user_id}", response_model=UserDTO)
async def delete_by_id(
    service: AuthDep, user: Annotated[User, Depends(get_user_by_id)]
) -> Any:
    return await service.delete(user)


@router.get("/users/", response_model=PageDTO[UserDTO])
async def get_many(
    service: AuthDep,
    pagination: Annotated[LimitOffset, Depends()],
    sorting: Annotated[Sorting, Depends()],
) -> Any:
    return await service.get_many(pagination, sorting)


@router.post("/users/{user_id}/grant", response_model=UserDTO)
async def grant(
    service: AuthDep,
    user: Annotated[User, Depends(get_user_by_id)],
) -> Any:
    return await service.grant_superuser(user)


@router.post("/users/{user_id}/revoke", response_model=UserDTO)
async def revoke(
    service: AuthDep,
    user: Annotated[User, Depends(get_user_by_id)],
) -> Any:
    return await service.revoke_superuser(user)