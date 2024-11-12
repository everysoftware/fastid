from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.auth.permissions import Requires
from app.authlib.dependencies import UserDep
from app.domain.pagination import LimitOffset, Page
from app.domain.sorting import Sorting
from app.social_login.dependencies import SocialLoginDep, get_account
from app.social_login.schemas import OAuthAccount

router = APIRouter(prefix="/oauth/accounts", tags=["OAuth"])


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
)
def get(
    account: Annotated[OAuthAccount, Depends(get_account)],
) -> OAuthAccount:
    return account


@router.delete(
    "/{account_id}",
    dependencies=[Depends(Requires(is_oauth=False))],
    status_code=status.HTTP_200_OK,
)
async def disconnect(
    service: SocialLoginDep,
    user: UserDep,
    account: Annotated[OAuthAccount, Depends(get_account)],
) -> OAuthAccount:
    return await service.disconnect(user, account)


@router.get("/", status_code=status.HTTP_200_OK)
async def paginate(
    service: SocialLoginDep,
    user: UserDep,
    pagination: Annotated[LimitOffset, Depends()],
    sorting: Annotated[Sorting, Depends()],
) -> Page[OAuthAccount]:
    return await service.paginate(user, pagination, sorting)
