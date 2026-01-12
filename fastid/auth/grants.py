from abc import abstractmethod
from typing import Any

from fastlink.exceptions import FastLinkError
from fastlink.jwt.schemas import JWTPayload
from fastlink.schemas import (
    OAuth2AuthorizationCodeRequest,
    OAuth2Callback,
    OAuth2PasswordRequest,
    OAuth2RefreshTokenRequest,
    TokenResponse,
)

from fastid.apps.exceptions import (
    InvalidAuthorizationCodeError,
    InvalidClientCredentialsError,
)
from fastid.apps.models import App
from fastid.apps.repositories import AppClientIDSpecification
from fastid.auth.config import auth_settings
from fastid.auth.exceptions import (
    EmailNotFoundError,
    InvalidTokenError,
    NoPermissionError,
    NotSupportedResponseTypeError,
)
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.auth.schemas import OAuth2ConsentRequest
from fastid.cache.dependencies import CacheDep
from fastid.cache.exceptions import KeyNotFoundError
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.utils import UUIDv7
from fastid.security.crypto import generate_otp
from fastid.security.jwt import jwt_backend


class Grant(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow
        self.token_backend = jwt_backend

    @abstractmethod
    async def authorize(self, form: Any) -> TokenResponse: ...

    async def validate_client(self, client_id: str) -> App:
        try:
            return await self.uow.apps.find(AppClientIDSpecification(client_id))
        except NoResultFoundError as e:
            raise InvalidClientCredentialsError from e

    async def authenticate_client(self, client_id: str, client_secret: str) -> App:
        app = await self.validate_client(client_id)
        app.verify_secret(client_secret)
        return app

    def grant(self, user: User, scope: str) -> TokenResponse:
        if "admin" in scope and not user.is_superuser:
            raise NoPermissionError
        at = self.token_backend.create("access", JWTPayload(sub=str(user.id), scope=scope))
        if "openid" in scope:
            payload = JWTPayload(
                sub=str(user.id),
                name=user.display_name,
                given_name=user.first_name,
                family_name=user.last_name,
                email=user.email,
                email_verified=user.is_verified,
            )
            it = self.token_backend.create("id", payload)
        else:
            it = None
        if "offline_access" in scope:
            rt = self.token_backend.create("refresh", JWTPayload(sub=str(user.id), scope=scope))
        else:
            rt = None
        return TokenResponse(access_token=at, id_token=it, refresh_token=rt)


class PasswordGrant(Grant):
    async def authorize(self, form: OAuth2PasswordRequest) -> TokenResponse:
        try:
            user = await self.uow.users.find(EmailUserSpecification(form.username))
        except NoResultFoundError as e:
            raise EmailNotFoundError from e
        user.verify_password(form.password)
        return self.grant(user, form.scope)


class AuthorizationCodeGrant(Grant):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        super().__init__(uow)
        self.cache = cache

    async def validate_consent(self, consent: OAuth2ConsentRequest) -> OAuth2ConsentRequest:
        if consent.response_type != "code":
            raise NotSupportedResponseTypeError
        assert consent.client_id is not None
        assert consent.redirect_uri is not None
        app = await self.validate_client(consent.client_id)
        app.verify_redirect_uri(consent.redirect_uri)
        return consent

    async def approve_consent(self, consent: OAuth2ConsentRequest, user: User) -> str:
        code = generate_otp()
        await self.cache.set(
            f"ac:{consent.client_id}:{code}",
            f"{user.id}:{consent.scope}",
            expire=auth_settings.authorization_code_expires_in,
        )
        callback = OAuth2Callback(code=code, state=consent.state, redirect_uri=consent.redirect_uri)
        return callback.get_url()

    async def authorize(self, form: OAuth2AuthorizationCodeRequest) -> TokenResponse:
        await self.authenticate_client(form.client_id, form.client_secret)
        try:
            data = await self.cache.pop(f"ac:{form.client_id}:{form.code}")
        except KeyNotFoundError as e:
            raise InvalidAuthorizationCodeError from e
        user_id, scope = data.split(":")
        user = await self.uow.users.get(UUIDv7(user_id))
        return self.grant(user, scope)


class RefreshTokenGrant(Grant):
    async def authorize(
        self,
        form: OAuth2RefreshTokenRequest,
    ) -> TokenResponse:
        await self.authenticate_client(form.client_id, form.client_secret)
        try:
            content = self.token_backend.validate("refresh", form.refresh_token)
        except FastLinkError as e:
            raise InvalidTokenError from e
        assert content.scope is not None
        user = await self.uow.users.get(UUIDv7(content.sub))
        return self.grant(user, content.scope)
