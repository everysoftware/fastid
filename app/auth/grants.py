from abc import abstractmethod
from typing import Any

from app.apps.exceptions import (
    InvalidClientCredentials,
    InvalidAuthorizationCode,
)
from app.apps.models import App
from app.apps.repositories import IsActiveApp
from app.auth.config import auth_settings
from app.auth.exceptions import (
    NotSupportedResponseType,
    NoPermission,
    UserEmailNotFound,
)
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.dependencies import token_backend
from app.authlib.oauth import (
    TokenResponse,
    OAuth2PasswordRequest,
    OAuth2AuthorizationCodeRequest,
    OAuth2RefreshTokenRequest,
    OAuth2Callback,
)
from app.base.service import UseCase
from app.base.types import UUID
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.utils.otp import otp


class Grant(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow
        self.token_backend = token_backend

    @abstractmethod
    async def authorize(self, form: Any) -> TokenResponse: ...

    async def validate_client(self, client_id: str) -> App:
        app = await self.uow.apps.find(IsActiveApp(client_id))
        if app is None:
            raise InvalidClientCredentials()
        return app

    async def authenticate_client(
        self, client_id: str, client_secret: str
    ) -> App:
        app = await self.validate_client(client_id)
        app.verify_secret(client_secret)
        return app

    def grant(self, user: User, scope: str) -> TokenResponse:
        if "admin" in scope and not user.is_superuser:
            raise NoPermission()
        at = self.token_backend.create_at(user.id, scope=scope)
        if "openid" in scope:
            it = self.token_backend.create_it(
                user.id,
                name=user.display_name,
                given_name=user.first_name,
                family_name=user.last_name,
                email=user.email,
                email_verified=user.is_verified,
            )
        else:
            it = None
        if "offline_access" in scope:
            rt = self.token_backend.create_rt(user.id, scope=scope)
        else:
            rt = None
        return self.token_backend.to_response(at=at, rt=rt, it=it)


class PasswordGrant(Grant):
    async def authorize(self, form: OAuth2PasswordRequest) -> TokenResponse:
        user = await self.uow.users.find(IsActiveUser(form.username))
        if user is None:
            raise UserEmailNotFound()
        user.verify_password(form.password)
        return self.grant(user, form.scope)


class AuthorizationCodeGrant(Grant):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        super().__init__(uow)
        self.cache = cache

    async def validate_consent(
        self, consent: OAuth2ConsentRequest
    ) -> OAuth2ConsentRequest:
        if consent.response_type != "code":
            raise NotSupportedResponseType()
        assert consent.client_id is not None
        assert consent.redirect_uri is not None
        app = await self.validate_client(consent.client_id)
        app.verify_redirect_uri(consent.redirect_uri)
        return consent

    async def approve_consent(
        self, consent: OAuth2ConsentRequest, user: User
    ) -> str:
        code = otp()
        await self.cache.set(
            f"ac:{consent.client_id}:{code}",
            f"{user.id}:{consent.scope}",
            expire=auth_settings.authorization_code_expires_in,
        )
        callback = OAuth2Callback(
            code=code, state=consent.state, redirect_uri=consent.redirect_uri
        )
        return callback.get_url()

    async def authorize(
        self, form: OAuth2AuthorizationCodeRequest
    ) -> TokenResponse:
        await self.authenticate_client(form.client_id, form.client_secret)
        data = await self.cache.get(
            f"ac:{form.client_id}:{form.code}", cast=str
        )
        await self.cache.delete(f"ac:{form.client_id}:{form.code}")
        if data is None:
            raise InvalidAuthorizationCode()
        user_id, scope = data.split(":")
        user = await self.uow.users.get_one(UUID(user_id))
        return self.grant(user, scope)


class RefreshTokenGrant(Grant):
    async def authorize(
        self,
        form: OAuth2RefreshTokenRequest,
    ) -> TokenResponse:
        await self.authenticate_client(form.client_id, form.client_secret)
        content = self.token_backend.validate_rt(form.refresh_token)
        assert content.scope is not None
        user = await self.uow.users.get_one(UUID(content.sub))
        return self.grant(user, content.scope)
