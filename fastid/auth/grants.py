from abc import abstractmethod
from typing import Any

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
from fastid.auth.schemas import AuthorizationResponse, OAuth2ConsentRequest, PayloadResponse, UserDTO
from fastid.cache.dependencies import CacheDep
from fastid.cache.exceptions import KeyNotFoundError
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.utils import UUIDv7, uuid
from fastid.security.crypto import generate_otp
from fastid.security.exceptions import JWTError
from fastid.security.jwt import jwt_backend
from fastid.security.schemas import JWTPayload


class Grant(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow
        self.token_backend = jwt_backend

    @abstractmethod
    async def authorize(self, form: Any) -> AuthorizationResponse: ...

    async def validate_client(self, client_id: str) -> App:
        try:
            return await self.uow.apps.find(AppClientIDSpecification(client_id))
        except NoResultFoundError as e:
            raise InvalidClientCredentialsError from e

    async def authenticate_client(self, client_id: str, client_secret: str) -> App:
        app = await self.validate_client(client_id)
        app.verify_secret(client_secret)
        return app

    def grant(self, user: User, scope: str) -> AuthorizationResponse:
        tokens = self.issue_tokens(user, scope)
        return self.get_auth_response(user, scope, tokens)

    def issue_tokens(self, user: User, scope: str) -> dict[str, dict[str, Any]]:
        self._check_scope(user, scope)
        tokens = {
            token_type: {"is_issued": False, "token": None, "payload": None}
            for token_type in ["access", "refresh", "id"]
        }
        self._issue_at(user, scope, tokens)
        if "offline_access" in scope:
            self._issue_rt(user, scope, tokens)
        if "openid" in scope:
            self._issue_it(user, tokens)
        return tokens

    def get_auth_response(self, user: User, scope: str, tokens: dict[str, Any]) -> AuthorizationResponse:
        user_dto = UserDTO.model_validate(user)
        payload = PayloadResponse(
            access_token=tokens["access"]["payload"],
            id_token=tokens["id"]["payload"],
            refresh_token=tokens["refresh"]["payload"],
        )
        token_id = str(uuid())
        expires_in = self.token_backend.get_lifetime("access")
        token = TokenResponse(
            token_id=token_id,
            expires_in=expires_in,
            scope=scope,
            access_token=tokens["access"]["token"],
            id_token=tokens["id"]["token"],
            refresh_token=tokens["refresh"]["token"],
        )
        return AuthorizationResponse(user=user_dto, payload=payload, token=token)

    @staticmethod
    def _check_scope(user: User, scope: str) -> None:
        if "admin" in scope and not user.is_superuser:
            raise NoPermissionError

    def _issue_at(self, user: User, scope: str, tokens: dict[str, dict[str, Any]]) -> None:
        schema = JWTPayload(sub=str(user.id), scope=scope)
        token, payload = self.token_backend.create("access", schema)
        tokens["access"]["is_issued"] = True
        tokens["access"]["token"] = token
        tokens["access"]["payload"] = payload

    def _issue_rt(self, user: User, scope: str, tokens: dict[str, dict[str, Any]]) -> None:
        schema = JWTPayload(sub=str(user.id), scope=scope)
        token, payload = self.token_backend.create("refresh", schema)
        tokens["refresh"]["is_issued"] = True
        tokens["refresh"]["token"] = token
        tokens["refresh"]["payload"] = payload

    def _issue_it(self, user: User, tokens: dict[str, dict[str, Any]]) -> None:
        schema = JWTPayload(
            sub=str(user.id),
            name=user.display_name,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            email_verified=user.is_verified,
        )
        token, payload = self.token_backend.create("id", schema)
        tokens["id"]["is_issued"] = True
        tokens["id"]["token"] = token
        tokens["id"]["payload"] = payload


class PasswordGrant(Grant):
    async def authorize(self, form: OAuth2PasswordRequest) -> AuthorizationResponse:
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

    async def authorize(self, form: OAuth2AuthorizationCodeRequest) -> AuthorizationResponse:
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
    ) -> AuthorizationResponse:
        await self.authenticate_client(form.client_id, form.client_secret)
        try:
            content = self.token_backend.validate("refresh", form.refresh_token)
        except JWTError as e:
            raise InvalidTokenError from e
        assert content.scope is not None
        user = await self.uow.users.get(UUIDv7(content.sub))
        return self.grant(user, content.scope)
