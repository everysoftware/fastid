import asyncio
from abc import abstractmethod
from typing import Any

from fastid.apps.exceptions import (
    InvalidAuthorizationCodeError,
    InvalidClientCredentialsError,
)
from fastid.apps.repositories import AppClientIDSpecification
from fastid.apps.schemas import AppDTO, ClientSnapshot
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
from fastid.auth.server import ServerURLDep
from fastid.cache.dependencies import CacheDep
from fastid.cache.exceptions import KeyNotFoundError, LockError, LockLostError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import UUIDv7, uuid
from fastid.security.crypto import generate_otp
from fastid.security.exceptions import JWTError
from fastid.security.jwt import jwt_backend
from fastid.security.schemas import JWTPayload


_CLIENT_CACHE_LOCKS: dict[str, asyncio.Lock] = {}


class Grant(UseCase):
    def __init__(self, uow: UOWDep, cache: CacheDep, server_url: ServerURLDep) -> None:
        self.uow = uow
        self.cache = cache
        self.server_url = server_url
        self.token_backend = jwt_backend

    @abstractmethod
    async def authorize(self, form: Any) -> AuthorizationResponse: ...

    async def validate_client(self, client_id: str) -> ClientSnapshot:
        cache_key = f"apps:{client_id}"
        try:
            return ClientSnapshot.model_validate(await self.cache.get(cache_key))
        except KeyNotFoundError:
            pass
        except (RedisConnectionError, RedisTimeoutError) as exc:
            if not self._redis_pool_exhausted(exc):
                raise
            return await self._read_client_fresh(client_id)
        # Caller-owned transactions may contain uncommitted state; use them
        # directly rather than waiting for a distributed cache-fill lock.
        if self.uow.is_active and self.uow.session.in_transaction():
            return await self._read_client(self.uow, client_id)

        # Coalesce cold/expired cache misses inside this worker before they
        # reach Redis, so a burst performs one lock acquisition and DB read.
        local_lock = _CLIENT_CACHE_LOCKS.setdefault(cache_key, asyncio.Lock())
        async with local_lock:
            try:
                return ClientSnapshot.model_validate(await self.cache.get(cache_key))
            except KeyNotFoundError:
                pass
            except (RedisConnectionError, RedisTimeoutError) as exc:
                if not self._redis_pool_exhausted(exc):
                    raise
                return await self._read_client_fresh(client_id)
            try:
                async with self.cache.lock(cache_key, blocking=True, blocking_timeout=10, timeout=120) as lock:
                    try:
                        return ClientSnapshot.model_validate(await self.cache.get(cache_key))
                    except KeyNotFoundError:
                        pass
                    except (RedisConnectionError, RedisTimeoutError) as exc:
                        if not self._redis_pool_exhausted(exc):
                            raise
                        return await self._read_client_fresh(client_id)
                    async with SQLAlchemyUOW(self.uow.session_factory) as read_uow:
                        snapshot = await self._read_client(read_uow, client_id)
                    try:
                        await self.cache.set(
                            cache_key,
                            snapshot.model_dump(mode="json"),
                            expire=auth_settings.app_expires_in_seconds,
                            lock=lock,
                        )
                    except LockLostError:
                        return await self._read_client_fresh(client_id)
                    return snapshot
            except LockError:
                # Another worker may be filling this key. Preserve token
                # issuance if its distributed lock exceeds our bounded wait.
                return await self._read_client_fresh(client_id)
            except (RedisConnectionError, RedisTimeoutError) as exc:
                if not self._redis_pool_exhausted(exc):
                    raise
                return await self._read_client_fresh(client_id)

    @staticmethod
    def _redis_pool_exhausted(error: RedisConnectionError | RedisTimeoutError) -> bool:
        return isinstance(error, RedisTimeoutError) or str(error) == "No connection available."

    async def _read_client_fresh(self, client_id: str) -> ClientSnapshot:
        async with SQLAlchemyUOW(self.uow.session_factory) as read_uow:
            return await self._read_client(read_uow, client_id)

    @staticmethod
    async def _read_client(uow: SQLAlchemyUOW, client_id: str) -> ClientSnapshot:
        try:
            app = await uow.apps.find(AppClientIDSpecification(client_id))
        except NoResultFoundError as e:
            raise InvalidClientCredentialsError from e
        return ClientSnapshot.model_validate(app)

    async def authenticate_client(self, client_id: str, client_secret: str) -> ClientSnapshot:
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
        token, payload = self.token_backend.create("access", schema, issuer=self.server_url)
        tokens["access"]["is_issued"] = True
        tokens["access"]["token"] = token
        tokens["access"]["payload"] = payload

    def _issue_rt(self, user: User, scope: str, tokens: dict[str, dict[str, Any]]) -> None:
        schema = JWTPayload(sub=str(user.id), scope=scope)
        token, payload = self.token_backend.create("refresh", schema, issuer=self.server_url)
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
        token, payload = self.token_backend.create("id", schema, issuer=self.server_url)
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
            content = self.token_backend.validate("refresh", form.refresh_token, issuer=self.server_url)
        except JWTError as e:
            raise InvalidTokenError from e
        assert content.scope is not None
        user = await self.uow.users.get(UUIDv7(content.sub))
        return self.grant(user, content.scope)


class ClientCredentialsGrant(Grant):
    async def authorize_token(self, form: OAuth2ClientCredentialsRequest) -> TokenResponse:
        app = await self.authenticate_client(form.client_id, form.client_secret)
        self._check_app_scope(app, form.scope)
        tokens = await self._issue_app_tokens(app, form.scope)
        return self._get_token_response(form.scope, tokens)

    async def authorize(self, form: OAuth2ClientCredentialsRequest) -> AuthorizationResponse:
        app = await self.authenticate_client(form.client_id, form.client_secret)
        self._check_app_scope(app, form.scope)
        tokens = await self._issue_app_tokens(app, form.scope)
        return self._get_app_auth_response(form.scope, tokens, app)

    @staticmethod
    def _check_app_scope(app: ClientSnapshot, scope: str) -> None:
        pass

    async def _issue_app_tokens(self, app: ClientSnapshot, scope: str) -> dict[str, dict[str, Any]]:
        tokens: dict[str, Any] = {
            token_type: {"is_issued": False, "token": None, "payload": None}
            for token_type in ["access", "refresh", "id"]
        }
        schema = JWTPayload(sub=str(app.id), scope=scope)
        token, payload = await self.token_backend.create_async("access", schema, issuer=self.server_url)
        tokens["access"]["is_issued"] = True
        tokens["access"]["token"] = token
        tokens["access"]["payload"] = payload
        return tokens

    def _get_app_auth_response(self, scope: str, tokens: dict[str, Any], app: ClientSnapshot) -> AuthorizationResponse:
        app_dto = AppDTO.model_validate(app)
        payload = self._get_payload_response(tokens)
        token = self._get_token_response(scope, tokens)
        return AuthorizationResponse(app=app_dto, payload=payload, token=token, sub_type=SubscriberType.app)
