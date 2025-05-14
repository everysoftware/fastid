from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette import status

from fastid.apps.dependencies import AppsDep, get_app
from fastid.apps.models import App
from fastid.apps.schemas import AppCreate, AppDTO, AppUpdate
from fastid.auth.permissions import Requires

router = APIRouter(tags=["Apps"])


@router.post(
    "/apps",
    dependencies=[Depends(Requires(superuser=True))],
    response_model=AppDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create(service: AppsDep, app_in: AppCreate) -> Any:
    return await service.register(app_in)


@router.get(
    "/apps/{app_id}",
    dependencies=[Depends(Requires(superuser=True))],
    response_model=AppDTO,
    status_code=status.HTTP_200_OK,
)
def get(app: Annotated[App, Depends(get_app)]) -> Any:
    return app


@router.patch(
    "/apps/{app_id}",
    dependencies=[Depends(Requires(superuser=True))],
    response_model=AppDTO,
    status_code=status.HTTP_200_OK,
)
async def patch(service: AppsDep, app: Annotated[App, Depends(get_app)], app_update: AppUpdate) -> Any:
    return await service.update(app, app_update)


@router.delete(
    "/apps/{app_id}",
    dependencies=[Depends(Requires(superuser=True))],
    response_model=AppDTO,
    status_code=status.HTTP_200_OK,
)
async def delete(service: AppsDep, app: Annotated[App, Depends(get_app)]) -> Any:
    return await service.delete(app)
