from app.auth.models import User
from app.base.pagination import Pagination, Page
from app.base.service import UseCases
from app.base.sorting import Sorting
from app.base.types import UUID
from app.db.dependencies import UOWDep
from app.oauthlib.dependencies import OAuthName, OAuthDep
from app.oauthlib.schemas import OAuthCallback, OpenIDBearer
from app.social.exceptions import (
    OAuthAccountNotFound,
    OAuthAlreadyConnected,
)
from app.social.models import OAuthAccount
from app.social.repositories import (
    IsAccountBelongToUser,
    IsAccountConnected,
)


class SocialLoginUseCases(UseCases):
    def __init__(self, uow: UOWDep, oauth: OAuthDep) -> None:
        self.uow = uow
        self.oauth = oauth

    async def login(self, oauth_name: OAuthName) -> str:
        factory = self.oauth.get_factory(oauth_name)
        oauth = factory.create()
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
        await self.uow.commit()
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
        user.disconnect_open_id(account.provider)
        account = await self.uow.oauth_accounts.remove(account)
        await self.uow.commit()
        return account

    async def _callback(
        self, oauth_name: OAuthName, callback: OAuthCallback
    ) -> OpenIDBearer:
        factory = self.oauth.get_factory(oauth_name)
        oauth = factory.create()
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
        account.update(open_id)
        return await self.uow.users.get_one(account.user_id)
