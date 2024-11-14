from typing import Any

from fastapi import APIRouter
from starlette import status

from app.auth.dependencies import AuthDep, UserDep
from app.auth.schemas import UserDTO, UserUpdate, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO
)
async def register(
    service: AuthDep,
    dto: UserCreate,
) -> Any:
    return await service.register(dto)


@router.patch("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def patch(
    service: AuthDep,
    user: UserDep,
    dto: UserUpdate,
) -> Any:
    return await service.update(user, dto)


@router.delete("/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def delete(service: AuthDep, user: UserDep) -> Any:
    return await service.delete(user)
