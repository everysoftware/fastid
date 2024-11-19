from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette import status

from app.auth.dependencies import UserDep, user_dep
from app.base.pagination import PageDTO
from app.oauth.dependencies import OAuthAccountsDep, get_account
from app.oauth.schemas import OAuthAccountDTO

router = APIRouter(
    dependencies=[user_dep], prefix="/oauth/accounts", tags=["OAuth"]
)


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
)
def get(
    account: Annotated[OAuthAccountDTO, Depends(get_account)],
) -> OAuthAccountDTO:
    return account


@router.get(
    "/",
    response_model=PageDTO[OAuthAccountDTO],
    status_code=status.HTTP_200_OK,
)
async def paginate(
    service: OAuthAccountsDep,
    user: UserDep,
) -> Any:
    return await service.paginate(user)
