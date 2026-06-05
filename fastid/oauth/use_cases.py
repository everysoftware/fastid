import contextlib
from typing import Any, cast

from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.auth.schemas import OAuth2Callback, TokenResponse
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.schemas import LimitOffset, Page, Sorting
from fastid.integrations.config import integration_settings
from fastid.integrations.dependencies import OAuth2RegistryDep, TelegramWidgetDep
from fastid.integrations.schemas import TelegramCallback
from fastid.oauth.exceptions import (
    OAuthAccountInUseError,
    OAuthProviderDisabledError,
)
from fastid.oauth.models import OAuthAccount
from fastid.oauth.repositories import (
    ProviderAccountSpecification,
    UserAccountPageSpecification,
    UserAccountSpecification,
)
from fastid.oauth.schemas import InspectProviderResponse, OpenIDBearer
from fastid.security.jwt import jwt_backend
from fastid.security.schemas import JWTPayload


class OAuthUseCases(UseCase):
    def __init__(self, uow: UOWDep, registry: OAuth2RegistryDep, telegram_widget: TelegramWidgetDep) -> None:
        self.uow = uow
        self.registry = registry
        self.telegram_widget = telegram_widget

    async def get_login_url(self, provider: str) -> str:
        async with self._get_client(provider) as client:
            return cast(str, await client.login_url())

    async def inspect(self, provider: str) -> InspectProviderResponse:
        async with self._get_client(provider) as client:
            login_url = await client.login_url()
            return InspectProviderResponse(
                meta=client.meta,
                discovery=client.discovery,
                login_url=login_url,
            )

    async def login(self, provider: str, callback: OAuth2Callback | TelegramCallback) -> TokenResponse:
        open_id = await self._callback(provider, callback)
        try:
            account = await self.uow.oauth_accounts.find(ProviderAccountSpecification(open_id.provider, open_id.id))
        except NoResultFoundError:
            account = await self._register(open_id)
        user = await self.uow.users.get(account.user_id)
        await self.uow.commit()
        token_data = jwt_backend.create("access", JWTPayload(sub=str(user.id)))
        return TokenResponse(access_token=token_data[0])

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

    def _get_client(self, provider: str) -> Any:
        if provider == "telegram":
            if not integration_settings.telegram_widget_enabled:
                raise OAuthProviderDisabledError
            return self.telegram_widget
        return self.registry.get(provider)

    async def _callback(self, provider: str, callback: OAuth2Callback | TelegramCallback) -> OpenIDBearer:
        if provider == "telegram":
            assert isinstance(callback, TelegramCallback)
            return await self._telegram_callback(callback)
        assert isinstance(callback, OAuth2Callback)
        return await self._oauth2_callback(provider, callback)

    async def _oauth2_callback(self, provider: str, callback: OAuth2Callback) -> OpenIDBearer:
        async with self._get_client(provider) as client:
            token = await client.login(callback)
            userinfo = await client.userinfo()
            return OpenIDBearer(
                **userinfo.userinfo.model_dump(),
                **token.token.model_dump(),
                provider=provider,
            )

    async def _telegram_callback(self, callback: TelegramCallback) -> OpenIDBearer:
        async with self._get_client("telegram") as client:
            userinfo = await client.verify(callback)
            return OpenIDBearer(
                **userinfo.userinfo.model_dump(),
                provider="telegram",
            )

    async def _register(self, open_id: OpenIDBearer) -> OAuthAccount:
        user = None
        if open_id.email:
            with contextlib.suppress(NoResultFoundError):
                user = await self.uow.users.find(EmailUserSpecification(open_id.email))
        if user is None:
            user = User.from_open_id(open_id)
            user = await self.uow.users.add(user)
        else:
            user.connect_open_id(open_id)
        account = OAuthAccount.from_open_id(open_id, user.id)
        await self.uow.oauth_accounts.add(account)
        return account
