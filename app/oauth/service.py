from app.auth.backend import token_backend
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.authlib.oauth import TokenResponse
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
from app.oauth.providers import registry
from app.oauth.repositories import (
    IsAccountBelongToUser,
    IsAccountConnected,
    IsAccountExists,
)
from app.oauthlib.schemas import UniversalCallback, OpenIDBearer


class OAuthUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    @staticmethod
    async def get_authorization_url(oauth_name: str) -> str:
        async with registry.begin(oauth_name) as oauth:
            return oauth.get_authorization_url()

    async def authorize(
        self, oauth_name: str, callback: UniversalCallback
    ) -> TokenResponse:
        open_id = await self._callback(oauth_name, callback)
        account = await self.uow.oauth_accounts.find(
            IsAccountConnected(open_id.provider, open_id.id)
        )
        if not account:
            account = await self._register(open_id)
        user = await self.uow.users.get_one(account.user_id)
        await self.uow.commit()
        at = token_backend.create_at(user.id)
        return token_backend.to_response(at)

    async def connect(
        self, user: User, oauth_name: str, callback: UniversalCallback
    ) -> OAuthAccount:
        open_id = await self._callback(oauth_name, callback)
        account = await self.uow.oauth_accounts.find(
            IsAccountConnected(open_id.provider, open_id.id)
        )
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
            IsAccountBelongToUser(user.id),
            pagination=LimitOffset(limit=10),
            sorting=Sorting(),
        )

    async def revoke(self, user: User, oauth_name: str) -> OAuthAccount:
        account = await self.uow.oauth_accounts.find_one(
            IsAccountExists(user.id, oauth_name)
        )
        user.disconnect_open_id(account.provider)
        account = await self.uow.oauth_accounts.remove(account)
        await self.uow.commit()
        return account

    @staticmethod
    async def _callback(
        oauth_name: str, callback: UniversalCallback
    ) -> OpenIDBearer:
        async with registry.begin(oauth_name) as oauth:
            token = await oauth.authorize(callback)
            open_id = await oauth.userinfo()
            return OpenIDBearer(
                **token.model_dump(),
                **open_id.model_dump(),
            )

    async def _register(self, open_id: OpenIDBearer) -> OAuthAccount:
        user = (
            await self.uow.users.find(IsActiveUser(open_id.email))
            if open_id.email
            else None
        )
        if not user:
            user = User.from_open_id(open_id)
            user = await self.uow.users.add(user)
        account = OAuthAccount.from_open_id(open_id, user)
        await self.uow.oauth_accounts.add(account)
        return account
