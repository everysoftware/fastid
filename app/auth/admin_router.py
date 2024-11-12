from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_user_by_id, AuthDep
from app.auth.permissions import Requires
from app.auth.schemas import User, UserUpdate, Role
from app.domain.pagination import LimitOffset, Page
from app.domain.sorting import Sorting

router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(Requires(is_superuser=True))],
)


@router.get("/users/{user_id}")
def get_by_id(user: Annotated[User, Depends(get_user_by_id)]) -> User:
    return user


@router.patch("/users/{user_id}")
async def update_by_id(
    service: AuthDep,
    user: Annotated[User, Depends(get_user_by_id)],
    update: UserUpdate,
) -> User:
    return await service.update(user, update)


@router.delete("/users/{user_id}")
async def delete_by_id(
    service: AuthDep, user: Annotated[User, Depends(get_user_by_id)]
) -> User:
    return await service.delete(user)


@router.get("/users/")
async def get_many(
    service: AuthDep,
    pagination: Annotated[LimitOffset, Depends()],
    sorting: Annotated[Sorting, Depends()],
) -> Page[User]:
    return await service.get_many(pagination, sorting)


@router.post("/users/{user_id}/grant")
async def grant(
    service: AuthDep,
    user: Annotated[User, Depends(get_user_by_id)],
    role: Role = Role.user,
) -> User:
    return await service.grant(user, role)
