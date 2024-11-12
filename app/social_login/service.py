from app.auth.schemas import User
from app.db.dependencies import UOWDep
from app.domain.pagination import Page, Pagination
from app.domain.service import BaseUseCase
from app.domain.sorting import Sorting
from app.domain.types import UUID
from app.oauthlib.dependencies import OAuthName, OAuthDep
from app.oauthlib.schemas import OAuthCallback, OpenIDBearer
from app.social_login.exceptions import (
    OAuthAccountNotFound,
    OAuthAlreadyConnected,
)
from app.social_login.repositories import (
    IsAccountBelongToUser,
    IsAccountConnected,
)
from app.social_login.schemas import OAuthAccount


class SocialLoginUseCases(BaseUseCase):
    def __init__(self, uow: UOWDep, oauth: OAuthDep) -> None:
        self.uow = uow
        self.oauth = oauth

    async def login(self, oauth_name: OAuthName) -> str:
        oauth = self.oauth.get(oauth_name)
        return await oauth.login()

    async def authorize(
        self, oauth_name: OAuthName, callback: OAuthCallback
    ) -> User:
        open_id = await self._callback(oauth_name, callback)
        account = await self.uow.oauth_accounts.find(
            IsAccountConnected(open_id.provider, open_id.id)
        )
        if account:
            user = await self._authorize_existing(account, open_id)
        else:
            user = await self._authorize_new(open_id)
        return user

    async def connect(
        self, user: User, oauth_name: OAuthName, callback: OAuthCallback
    ) -> OAuthAccount:
        open_id = await self._callback(oauth_name, callback)
        account = await self.uow.oauth_accounts.find(
            IsAccountConnected(open_id.provider, open_id.id)
        )
        if account:
            raise OAuthAlreadyConnected()
        account = OAuthAccount.from_open_id(open_id, user)
        return await self.uow.oauth_accounts.add(account)

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
        pagination: Pagination,
        sorting: Sorting,
    ) -> Page[OAuthAccount]:
        return await self.uow.oauth_accounts.get_many(
            IsAccountBelongToUser(user.id),
            pagination=pagination,
            sorting=sorting,
        )

    async def disconnect(
        self, user: User, account: OAuthAccount
    ) -> OAuthAccount:
        if account.provider == "telegram":
            user.telegram_id = None
            await self.uow.users.update(user)
        return await self.uow.oauth_accounts.remove(account)

    async def _callback(
        self, oauth_name: OAuthName, callback: OAuthCallback
    ) -> OpenIDBearer:
        oauth = self.oauth.get(oauth_name)
        token = await oauth.callback(callback)
        open_id = await oauth.get_user()
        return OpenIDBearer(
            **token.model_dump(),
            **open_id.model_dump(),
        )

    async def _authorize_new(self, open_id: OpenIDBearer) -> User:
        user = User.from_open_id(open_id)
        user = await self.uow.users.add(user)
        account = OAuthAccount.from_open_id(open_id, user)
        await self.uow.oauth_accounts.add(account)
        return user

    async def _authorize_existing(
        self, account: OAuthAccount, open_id: OpenIDBearer
    ) -> User:
        account = account.update(open_id)
        account = await self.uow.oauth_accounts.update(account)
        return await self.uow.users.get_one(account.user_id)
