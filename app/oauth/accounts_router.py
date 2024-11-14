from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette import status

from app.auth.dependencies import UserDep, user_dep
from app.auth.permissions import Requires
from app.base.pagination import LimitOffset, PageDTO
from app.base.sorting import Sorting
from app.oauth.dependencies import SocialLoginDep, get_account
from app.oauth.models import OAuthAccount
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


@router.delete(
    "/{account_id}",
    dependencies=[Depends(Requires(is_oauth=False))],
    response_model=OAuthAccountDTO,
    status_code=status.HTTP_200_OK,
)
async def disconnect(
    service: SocialLoginDep,
    user: UserDep,
    account: Annotated[OAuthAccount, Depends(get_account)],
) -> Any:
    return await service.disconnect(user, account)


@router.get(
    "/",
    response_model=PageDTO[OAuthAccountDTO],
    status_code=status.HTTP_200_OK,
)
async def paginate(
    service: SocialLoginDep,
    user: UserDep,
    pagination: Annotated[LimitOffset, Depends()],
    sorting: Annotated[Sorting, Depends()],
) -> Any:
    return await service.paginate(user, pagination, sorting)