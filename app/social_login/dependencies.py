from typing import Annotated

from fastapi import Depends

from app.domain.types import UUID
from app.social_login.schemas import OAuthAccount
from app.social_login.service import SocialLoginUseCases

SocialLoginDep = Annotated[SocialLoginUseCases, Depends()]


async def get_account(
    service: SocialLoginDep, account_id: UUID
) -> OAuthAccount:
    return await service.get_one(account_id)
