from app.apps.exceptions import (
    InvalidClientCredentials,
    InvalidAuthorizationCode,
)
from app.apps.repositories import IsActiveApp
from app.auth.config import auth_settings
from app.auth.exceptions import (
    UserNotFound,
    UserAlreadyExists,
    NotSupportedGrant,
    NotSupportedResponseType,
)
from app.auth.models import User
from app.auth.repositories import IsActiveUser
from app.auth.schemas import (
    UserUpdate,
    UserCreate,
    OAuth2TokenRequest,
    OAuth2ConsentRequest,
)
from app.authlib.dependencies import token_backend
from app.authlib.oauth import (
    OAuth2Grant,
    OAuth2PasswordRequest,
    OAuth2RefreshTokenRequest,
    OAuth2Callback,
    OAuth2AuthorizationCodeRequest,
)
from app.authlib.schemas import TokenResponse
from app.base.pagination import Pagination, Page
from app.base.service import UseCases
from app.base.sorting import Sorting
from app.base.types import UUID
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.utils.otp import otp


class AuthUseCases(UseCases):
    def __init__(self, uow: UOWDep, cache: CacheDep) -> None:
        self.uow = uow
        self.cache = cache

    async def register(self, dto: UserCreate) -> User:
        user = await self.uow.users.find(IsActiveUser(dto.email))
        if user is not None:
            raise UserAlreadyExists()
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.uow.commit()
        return user

    async def authorize(self, form: OAuth2TokenRequest) -> TokenResponse:
        match form.grant_type:
            case OAuth2Grant.password:
                token = await self._authorize_password(
                    form.as_password_grant()
                )
            case OAuth2Grant.authorization_code:
                token = await self._authorize_code(
                    form.as_authorization_code_grant()
                )
            case OAuth2Grant.refresh_token:
                token = await self._refresh_token(
                    form.as_refresh_token_grant()
                )
            case _:
                raise NotSupportedGrant()
        return token

    async def validate_consent_request(
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

    async def approve_consent_request(
        self, consent: OAuth2ConsentRequest, user_id: UUID
    ) -> str:
        code = otp()
        await self.cache.set(
            f"ac:{consent.client_id}:{code}",
            str(user_id),
            expire=auth_settings.authorization_code_expires_in,
        )
        callback = OAuth2Callback(
            code=code, state=consent.state, redirect_uri=consent.redirect_uri
        )
        return callback.get_url()

    async def get_one(self, user_id: UUID) -> User:
        user = await self.get(user_id)
        if user is None:
            raise UserNotFound()
        return user

    async def get_userinfo(self, token: str) -> User:
        payload = token_backend.validate_at(token)
        return await self.get_one(UUID(payload.sub))

    async def get(self, user_id: UUID) -> User | None:
        return await self.uow.users.get(user_id)

    async def update(
        self,
        user: User,
        dto: UserUpdate,
    ) -> User:
        user.merge_model(dto)
        await self.uow.commit()
        return user

    async def delete(self, user: User) -> User:
        await self.uow.users.remove(user)
        await self.uow.commit()
        return user

    async def get_many(
        self, pagination: Pagination, sorting: Sorting
    ) -> Page[User]:
        return await self.uow.users.get_many(
            pagination=pagination, sorting=sorting
        )

    async def grant_superuser(self, user: User) -> User:
        user.grant_superuser()
        await self.uow.commit()
        return user

    async def revoke_superuser(self, user: User) -> User:
        user.revoke_superuser()
        await self.uow.commit()
        return user

    async def _authorize_password(
        self, form: OAuth2PasswordRequest
    ) -> TokenResponse:
        user = await self.uow.users.find(IsActiveUser(form.username))
        if user is None:
            raise UserNotFound()
        user.verify_password(form.password)
        user.verify_scopes(form.scopes)
        at = token_backend.create_at(user.id, scope=form.scope)
        return token_backend.to_response(at=at)

    @staticmethod
    async def _refresh_token(
        form: OAuth2RefreshTokenRequest,
    ) -> TokenResponse:
        content = token_backend.validate_rt(form.refresh_token)
        at = token_backend.create_at(content.sub, scope=content.scope)
        return token_backend.to_response(at=at)

    async def _authorize_code(
        self, form: OAuth2AuthorizationCodeRequest
    ) -> TokenResponse:
        app = await self.uow.apps.find(IsActiveApp(form.client_id))
        if app is None:
            raise InvalidClientCredentials()
        app.check_token_request(form)
        user_id = await self.cache.get(
            f"ac:{form.client_id}:{form.code}", cast=str
        )
        if user_id is None:
            raise InvalidAuthorizationCode()
        await self.cache.delete(f"ac:{form.client_id}:{form.code}")
        user = await self.uow.users.get_one(UUID(user_id))
        at = token_backend.create_at(user.id)
        it = token_backend.create_it(
            user.id,
            name=user.display_name,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            email_verified=user.is_verified,
        )
        return token_backend.to_response(at=at, it=it)
