import contextlib

from auth365.schemas import JWTPayload, OAuth2Callback, OpenIDBearer, TelegramCallback, TokenResponse

from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.base.datatypes import UUIDv7
from app.base.pagination import LimitOffset, Page
from app.base.service import UseCase
from app.base.sorting import Sorting
from app.db.dependencies import UOWDep
from app.db.exceptions import NoResultFoundError
from app.oauth.clients.dependencies import RegistryDep
from app.oauth.exceptions import (
    OAuthAccountInUseError,
    OAuthAccountNotFoundError,
)
from app.oauth.models import OAuthAccount
from app.oauth.repositories import (
    ProviderAccountSpecification,
    UserAccountPageSpecification,
    UserAccountSpecification,
)
from app.security.jwt import jwt_backend


class OAuthUseCases(UseCase):
    def __init__(self, uow: UOWDep, registry: RegistryDep) -> None:
        self.uow = uow
        self.registry = registry

    async def get_authorization_url(self, provider_name: str) -> str:
        async with self.registry.get(provider_name) as oauth:
            return await oauth.get_authorization_url()

    async def authorize(self, provider_name: str, callback: OAuth2Callback | TelegramCallback) -> TokenResponse:
        open_id = await self._callback(provider_name, callback)
        try:
            account = await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        except NoResultFoundError:
            account = await self._register(open_id)
        user = await self.uow.users.get(account.user_id)
        await self.uow.commit()
        at = jwt_backend.create("access", JWTPayload(sub=str(user.id)))
        return TokenResponse(access_token=at)

    async def connect(
        self,
        user: User,
        provider_name: str,
        callback: OAuth2Callback | TelegramCallback,
    ) -> OAuthAccount:
        open_id = await self._callback(provider_name, callback)
        try:
            await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        except NoResultFoundError:
            pass
        else:
            raise OAuthAccountInUseError
        account = OAuthAccount.from_open_id(open_id, user)
        account = await self.uow.oauth_accounts.add(account)
        await self.uow.commit()
        return account

    async def get_one(self, account_id: UUIDv7) -> OAuthAccount:
        try:
            return await self.uow.oauth_accounts.get(account_id)
        except NoResultFoundError as e:
            raise OAuthAccountNotFoundError from e

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
        account = await self.uow.oauth_accounts.find(UserAccountSpecification(user.id, provider_name))
        user.disconnect_open_id(account.provider)
        account = await self.uow.oauth_accounts.delete(account)
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
        user = None
        if open_id.email:
            with contextlib.suppress(NoResultFoundError):
                user = await self.uow.users.find(UserEmailSpecification(open_id.email))
        if user is None:
            user = User.from_open_id(open_id)
            user = await self.uow.users.add(user)
        else:
            user.connect_open_id(open_id)
        account = OAuthAccount.from_open_id(open_id, user)
        await self.uow.oauth_accounts.add(account)
        return account
