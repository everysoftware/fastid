import contextlib

from fastlink.jwt.schemas import JWTPayload
from fastlink.schemas import OAuth2Callback, TokenResponse
from fastlink.telegram.schemas import TelegramCallback

from fastid.auth.models import User
from fastid.auth.repositories import UserEmailSpecification
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.schemas import LimitOffset, Page, Sorting
from fastid.oauth.clients.dependencies import RegistryDep
from fastid.oauth.exceptions import (
    OAuthAccountInUseError,
)
from fastid.oauth.models import OAuthAccount
from fastid.oauth.repositories import (
    ProviderAccountSpecification,
    UserAccountPageSpecification,
    UserAccountSpecification,
)
from fastid.oauth.schemas import InspectProviderResponse, OpenIDBearer
from fastid.security.jwt import jwt_backend


class OAuthUseCases(UseCase):
    def __init__(self, uow: UOWDep, registry: RegistryDep) -> None:
        self.uow = uow
        self.registry = registry

    async def inspect(self, provider: str) -> InspectProviderResponse:
        async with self.registry.get(provider) as session:
            login_url = await session.login_url()
            return InspectProviderResponse(
                meta=session.meta,
                login_url=login_url,
            )

    async def get_login_url(self, provider: str) -> str:
        async with self.registry.get(provider) as session:
            return await session.login_url()

    async def login(self, provider: str, callback: OAuth2Callback | TelegramCallback) -> TokenResponse:
        open_id = await self._callback(provider, callback)
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
        provider: str,
        callback: OAuth2Callback | TelegramCallback,
    ) -> OAuthAccount:
        open_id = await self._callback(provider, callback)
        try:
            await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        except NoResultFoundError:
            pass
        else:
            raise OAuthAccountInUseError
        account = OAuthAccount.from_open_id(open_id, user.id)
        account = await self.uow.oauth_accounts.add(account)
        await self.uow.commit()
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

    async def revoke(self, user: User, provider: str) -> OAuthAccount:
        account = await self.uow.oauth_accounts.find(UserAccountSpecification(user.id, provider))
        user.disconnect_open_id(account.provider)
        account = await self.uow.oauth_accounts.delete(account)
        await self.uow.commit()
        return account

    async def _callback(self, provider: str, callback: OAuth2Callback | TelegramCallback) -> OpenIDBearer:
        if provider == "telegram":
            assert isinstance(callback, TelegramCallback)
            return await self._telegram_callback(callback)
        assert isinstance(callback, OAuth2Callback)
        return await self._oauth2_callback(provider, callback)

    async def _oauth2_callback(self, provider: str, callback: OAuth2Callback) -> OpenIDBearer:
        async with self.registry.get(provider) as session:
            token = await session.login(callback)
            openid = await session.openid()
            return OpenIDBearer(
                **openid.model_dump(),
                **token.model_dump(),
                provider=provider,
            )

    async def _telegram_callback(self, callback: TelegramCallback) -> OpenIDBearer:
        async with self.registry.get("telegram") as session:
            openid = await session.callback(callback)  # type: ignore[arg-type]
            return OpenIDBearer(
                **openid.model_dump(),
                provider="telegram",
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
        account = OAuthAccount.from_open_id(open_id, user.id)
        await self.uow.oauth_accounts.add(account)
        return account
