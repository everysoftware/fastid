from abc import abstractmethod
from typing import Any

from fastid.apps.exceptions import (
    InvalidAuthorizationCodeError,
    InvalidClientCredentialsError,
)
from fastid.apps.models import App
from fastid.apps.repositories import AppClientIDSpecification
from fastid.apps.schemas import AppDTO
from fastid.auth.config import auth_settings
from fastid.auth.exceptions import (
    EmailNotFoundError,
    InvalidTokenError,
    NoPermissionError,
    NotSupportedResponseTypeError,
)
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.auth.schemas import (
    AuthorizationResponse,
    OAuth2AuthorizationCodeRequest,
    OAuth2Callback,
    OAuth2ClientCredentialsRequest,
    OAuth2ConsentRequest,
    OAuth2PasswordRequest,
    OAuth2RefreshTokenRequest,
    PayloadResponse,
    SubscriberType,
    TokenResponse,
    UserDTO,
)
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
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache
        self.token_backend = jwt_backend

    @abstractmethod
    async def authorize(self, form: Any) -> AuthorizationResponse: ...

    async def validate_client(self, client_id: str) -> App:
        cache_key = f"apps:{client_id}"
        try:
            cached = await self.cache.get(cache_key)
        except KeyNotFoundError:
            try:
                app = await self.uow.apps.find(AppClientIDSpecification(client_id))
            except NoResultFoundError as e:
                raise InvalidClientCredentialsError from e
            app_dict = app.dump()
            await self.cache.set(
                cache_key,
                app_dict,
                expire=auth_settings.app_expires_in_seconds,
            )
        else:
            app = App(**cached)
        return app

    async def authenticate_client(self, client_id: str, client_secret: str) -> App:
        app = await self.validate_client(client_id)
        app.verify_secret(client_secret)
        return app

    def grant(self, user: User, scope: str) -> AuthorizationResponse:
        tokens = self._issue_tokens(user, scope)
        return self._get_auth_response(scope, tokens, user)

    def _issue_tokens(self, user: User, scope: str) -> dict[str, dict[str, Any]]:
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

    def _get_auth_response(self, scope: str, tokens: dict[str, Any], user: User) -> AuthorizationResponse:
        user_dto = UserDTO.model_validate(user)
        payload = self._get_payload_response(tokens)
        token = self._get_token_response(scope, tokens)
        return AuthorizationResponse(user=user_dto, payload=payload, token=token)

    @staticmethod
    def _check_scope(user: User, scope: str) -> None:
        if "admin" in scope and not user.is_superuser:
            raise NoPermissionError

    @staticmethod
    def _get_payload_response(tokens: dict[str, Any]) -> PayloadResponse:
        return PayloadResponse(
            access_token=tokens["access"]["payload"],
            id_token=tokens["id"]["payload"],
            refresh_token=tokens["refresh"]["payload"],
        )

    def _get_token_response(self, scope: str, tokens: dict[str, Any]) -> TokenResponse:
        token_id = str(uuid())
        expires_in = self.token_backend.get_lifetime("access")
        return TokenResponse(
            token_id=token_id,
            expires_in=expires_in,
            scope=scope,
            access_token=tokens["access"]["token"],
            id_token=tokens["id"]["token"],
            refresh_token=tokens["refresh"]["token"],
        )

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
        user = await self._find_by_email(form.username)
        await user.verify_password(form.password)
        return self.grant(user, form.scope)

    async def _find_by_email(self, email: str) -> User:
        try:
            return await self.uow.users.find(EmailUserSpecification(email))
        except NoResultFoundError as e:
            raise EmailNotFoundError from e


class AuthorizationCodeGrant(Grant):
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


class ClientCredentialsGrant(Grant):
    async def authorize(self, form: OAuth2ClientCredentialsRequest) -> AuthorizationResponse:
        app = await self.authenticate_client(form.client_id, form.client_secret)
        self._check_app_scope(app, form.scope)
        tokens = await self._issue_app_tokens(app, form.scope)
        return self._get_app_auth_response(form.scope, tokens, app)

    @staticmethod
    def _check_app_scope(app: App, scope: str) -> None:
        pass

    async def _issue_app_tokens(self, app: App, scope: str) -> dict[str, dict[str, Any]]:
        tokens: dict[str, Any] = {
            token_type: {"is_issued": False, "token": None, "payload": None}
            for token_type in ["access", "refresh", "id"]
        }
        schema = JWTPayload(sub=str(app.id), scope=scope)
        token, payload = await self.token_backend.create_async("access", schema)
        tokens["access"]["is_issued"] = True
        tokens["access"]["token"] = token
        tokens["access"]["payload"] = payload
        return tokens

    def _get_app_auth_response(self, scope: str, tokens: dict[str, Any], app: App) -> AuthorizationResponse:
        app_dto = AppDTO.model_validate(app)
        payload = self._get_payload_response(tokens)
        token = self._get_token_response(scope, tokens)
        return AuthorizationResponse(app=app_dto, payload=payload, token=token, sub_type=SubscriberType.app)
