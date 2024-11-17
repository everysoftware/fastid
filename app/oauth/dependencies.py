from typing import Annotated

from fastapi import Depends

from app.base.types import UUID
from app.oauth.models import OAuthAccount
from app.oauth.service import OAuthUseCases

SocialLoginDep = Annotated[OAuthUseCases, Depends()]


async def get_account(
    service: SocialLoginDep, account_id: UUID
) -> OAuthAccount:
    return await service.get_one(account_id)
