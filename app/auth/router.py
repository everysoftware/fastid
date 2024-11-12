from fastapi import APIRouter
from starlette import status

from app.authlib.dependencies import UserDep
from app.auth.dependencies import AuthDep
from app.auth.schemas import User, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> User:
    return user


@router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    service: AuthDep,
    user: UserDep,
    dto: UserUpdate,
) -> User:
    return await service.update(user, dto)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(service: AuthDep, user: UserDep) -> User:
    return await service.delete(user)
