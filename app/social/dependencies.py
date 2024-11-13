from typing import Annotated

from fastapi import Depends

from app.base.types import UUID
from app.social.models import OAuthAccount
from app.social.service import SocialLoginUseCases

SocialLoginDep = Annotated[SocialLoginUseCases, Depends()]


async def get_account(
    service: SocialLoginDep, account_id: UUID
) -> OAuthAccount:
    return await service.get_one(account_id)
