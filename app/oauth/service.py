from auth365.schemas import TelegramCallback, OAuth2Callback, OpenIDBearer, JWTPayload, TokenResponse

from app.auth.backend import token_backend
from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.base.pagination import Page, LimitOffset
from app.base.service import UseCase
from app.base.sorting import Sorting
from app.base.types import UUID
from app.db.dependencies import UOWDep
from app.oauth.exceptions import (
    OAuthAccountNotFound,
    OAuthAccountInUse,
)
from app.oauth.models import OAuthAccount
from app.oauth.providers import RegistryDep
from app.oauth.repositories import (
    UserAccountPageSpecification,
    ProviderAccountSpecification,
    UserAccountSpecification,
)


class OAuthUseCases(UseCase):
    def __init__(self, uow: UOWDep, registry: RegistryDep) -> None:
        self.uow = uow
        self.registry = registry

    async def get_authorization_url(self, provider_name: str) -> str:
        async with self.registry.get(provider_name) as oauth:
            return await oauth.get_authorization_url()

    async def authorize(self, provider_name: str, callback: OAuth2Callback | TelegramCallback) -> TokenResponse:
        open_id = await self._callback(provider_name, callback)
        account = await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        if not account:
            account = await self._register(open_id)
        user = await self.uow.users.get_one(account.user_id)
        await self.uow.commit()
        at = token_backend.create("access", JWTPayload(sub=str(user.id)))
        return TokenResponse(access_token=at)

    async def connect(
        self,
        user: User,
        provider_name: str,
        callback: OAuth2Callback | TelegramCallback,
    ) -> OAuthAccount:
        open_id = await self._callback(provider_name, callback)
        account = await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        if account:
            raise OAuthAccountInUse()
        account = OAuthAccount.from_open_id(open_id, user)
        account = await self.uow.oauth_accounts.add(account)
        await self.uow.commit()
        return account

    async def get(self, account_id: UUID) -> OAuthAccount | None:
        return await self.uow.oauth_accounts.get(account_id)

    async def get_one(self, account_id: UUID) -> OAuthAccount:
        account = await self.get(account_id)
        if not account:
            raise OAuthAccountNotFound()
        return account

    async def paginate(
        self,
        user: User,
    ) -> Page[OAuthAccount]:
        return await self.uow.oauth_accounts.get_many(
            UserAccountPageSpecification(user.id),
            pagination=LimitOffset(limit=10),
            sorting=Sorting(),
        )

    async def revoke(self, user: User, provider_name: str) -> OAuthAccount:
        account = await self.uow.oauth_accounts.find_one(UserAccountSpecification(user.id, provider_name))
        user.disconnect_open_id(account.provider)
        account = await self.uow.oauth_accounts.remove(account)
        await self.uow.commit()
        return account

    async def _callback(self, provider_name: str, callback: OAuth2Callback | TelegramCallback) -> OpenIDBearer:
        async with self.registry.get(provider_name) as oauth:
            token = await oauth.authorize(callback)
            open_id = await oauth.userinfo()
            return OpenIDBearer(
                **token.model_dump(),
                **open_id.model_dump(),
            )

    async def _register(self, open_id: OpenIDBearer) -> OAuthAccount:
        user = await self.uow.users.find(UserEmailSpecification(open_id.email)) if open_id.email else None
        if user:
            user.connect_open_id(open_id)
        else:
            user = User.from_open_id(open_id)
            user = await self.uow.users.add(user)
        account = OAuthAccount.from_open_id(open_id, user)
        await self.uow.oauth_accounts.add(account)
        return account
