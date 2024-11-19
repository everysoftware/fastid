from abc import ABC, abstractmethod
from typing import Any

from app.apps.exceptions import (
    InvalidClientCredentials,
    InvalidAuthorizationCode,
)
from app.apps.repositories import IsActiveApp
from app.auth.config import auth_settings
from app.auth.exceptions import UserNotFound, NotSupportedResponseType
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
from app.base.types import UUID
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.utils.otp import otp


class Grant(ABC):
    @abstractmethod
    async def authorize(self, form: Any) -> TokenResponse: ...

    @staticmethod
    def grant(user: User, scope: str) -> TokenResponse:
        at = token_backend.create_at(user.id, scope=scope)
        if "openid" in scope:
            it = token_backend.create_it(
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
            rt = token_backend.create_rt(user.id, scope=scope)
        else:
            rt = None
        return token_backend.to_response(at=at, rt=rt, it=it)


class PasswordGrant(Grant):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def authorize(self, form: OAuth2PasswordRequest) -> TokenResponse:
        user = await self.uow.users.find(IsActiveUser(form.username))
        if user is None:
            raise UserNotFound()
        user.verify_password(form.password)
        return self.grant(user, form.scope)


class AuthorizationCodeGrant(Grant):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache

    async def validate_consent(
        self, consent: OAuth2ConsentRequest
    ) -> OAuth2ConsentRequest:
        if consent.response_type != "code":
            raise NotSupportedResponseType()
        if consent.client_id is None:
            raise InvalidClientCredentials()
        app = await self.uow.apps.find(IsActiveApp(consent.client_id))
        if app is None:
            raise InvalidClientCredentials()
        app.check_consent_request(consent)
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
        app = await self.uow.apps.find(IsActiveApp(form.client_id))
        if app is None:
            raise InvalidClientCredentials()
        app.check_token_request(form)
        data = await self.cache.get(
            f"ac:{form.client_id}:{form.code}", cast=str
        )
        if data is None:
            raise InvalidAuthorizationCode()
        await self.cache.delete(f"ac:{form.client_id}:{form.code}")
        user_id, scope = data.split(":")
        user = await self.uow.users.get_one(UUID(user_id))
        return self.grant(user, scope)


class RefreshTokenGrant(Grant):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def authorize(
        self,
        form: OAuth2RefreshTokenRequest,
    ) -> TokenResponse:
        content = token_backend.validate_rt(form.refresh_token)
        assert content.scope is not None
        user = await self.uow.users.get_one(UUID(content.sub))
        return self.grant(user, content.scope)
