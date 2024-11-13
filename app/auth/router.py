from typing import Any

from fastapi import APIRouter
from starlette import status

from app.auth.dependencies import AuthDep
from app.auth.schemas import UserDTO, UserUpdate
from app.authlib.dependencies import UserDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
def me(user: UserDep) -> Any:
    return user


@router.patch("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def patch(
    service: AuthDep,
    user: UserDep,
    dto: UserUpdate,
) -> Any:
    return await service.update_profile(user, dto)


@router.delete("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def delete(service: AuthDep, user: UserDep) -> Any:
    return await service.delete(user)
