from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Form, status
from starlette.responses import Response

from fastid.auth.dependencies import AuthDep, UserDep, cookie_transport, vt_transport
from fastid.auth.exceptions import NotSupportedGrantError
from fastid.auth.grants import (
    AuthorizationCodeGrant,
    ClientCredentialsGrant,
    Grant,
    PasswordGrant,
    RefreshTokenGrant,
)
from fastid.auth.schemas import (
    OAuth2AuthorizationCodeRequest,
    OAuth2ClientCredentialsRequest,
    OAuth2Grant,
    OAuth2PasswordRequest,
    OAuth2RefreshTokenRequest,
    OAuth2TokenRequest,
    SubscriberType,
    TokenResponse,
    UserCreate,
    UserDTO,
)
from fastid.auth.server import ServerURLDep
from fastid.cache.dependencies import CacheDep
from fastid.database.dependencies import UOWRawDep
from fastid.database.uow import SQLAlchemyUOW
from fastid.notify.dependencies import NotifyDep
from fastid.notify.schemas import PushNotificationRequest
from fastid.webhooks.dependencies import WebhooksDep
from fastid.webhooks.models import WebhookType
from fastid.webhooks.schemas import SendWebhookRequest
from fastid.webhooks.senders.dependencies import SenderDep
from fastid.webhooks.use_cases import WebhookUseCases

router = APIRouter(tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO)
async def register(
    service: AuthDep,
    notify: NotifyDep,
    webhooks: WebhooksDep,
    dto: UserCreate,
    background: BackgroundTasks,
) -> Any:
    user = await service.register(dto)
    notification = PushNotificationRequest(template="welcome")
    background.add_task(notify.push, user, notification)  # pragma: nocover
    webhook = SendWebhookRequest(
        type=WebhookType.user_registration, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user  # pragma: nocover


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def login(
    form: Annotated[OAuth2PasswordRequest, Form()],
    password_grant: Annotated[PasswordGrant, Depends()],
    webhooks: WebhooksDep,
    background: BackgroundTasks,
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            auth_data = await password_grant.authorize(OAuth2PasswordRequest.model_validate(form))
        case _:
            raise NotSupportedGrantError
    assert auth_data.user is not None
    webhook = SendWebhookRequest(type=WebhookType.user_login, payload={"user": auth_data.user.model_dump(mode="json")})
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return cookie_transport.get_login_response(auth_data.token)


async def get_token_grant(
    form: Annotated[OAuth2TokenRequest, Form()],
    uow: UOWRawDep,
    cache: CacheDep,
    server_url: ServerURLDep,
) -> AsyncIterator[Grant]:
    grant_types: dict[
        OAuth2Grant,
        type[PasswordGrant | AuthorizationCodeGrant | RefreshTokenGrant | ClientCredentialsGrant],
    ] = {
        OAuth2Grant.password: PasswordGrant,
        OAuth2Grant.authorization_code: AuthorizationCodeGrant,
        OAuth2Grant.refresh_token: RefreshTokenGrant,
        OAuth2Grant.client_credentials: ClientCredentialsGrant,
    }
    grant_type = grant_types.get(form.grant_type)
    if grant_type is None:
        raise NotSupportedGrantError
    grant = grant_type(uow, cache, server_url)
    if isinstance(grant, ClientCredentialsGrant):
        yield grant
    else:
        async with uow:
            yield grant


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def authorize(
    form: Annotated[OAuth2TokenRequest, Form()],
    grant: Annotated[Grant, Depends(get_token_grant)],
    sender: SenderDep,
    background: BackgroundTasks,
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            auth_data = await grant.authorize(OAuth2PasswordRequest.model_validate(form))
        case OAuth2Grant.authorization_code:
            auth_data = await grant.authorize(OAuth2AuthorizationCodeRequest.model_validate(form))
        case OAuth2Grant.refresh_token:
            auth_data = await grant.authorize(OAuth2RefreshTokenRequest.model_validate(form))
        case OAuth2Grant.client_credentials:
            assert isinstance(grant, ClientCredentialsGrant)
            return await grant.authorize_token(OAuth2ClientCredentialsRequest.model_validate(form))
        case _:
            raise NotSupportedGrantError
    if auth_data.sub_type == SubscriberType.user and auth_data.user is not None:
        webhook = SendWebhookRequest(
            type=WebhookType.user_login, payload={"user": auth_data.user.model_dump(mode="json")}
        )
        webhooks = WebhookUseCases(SQLAlchemyUOW(grant.uow.session_factory), grant.cache, sender)
        background.add_task(webhooks.send, webhook)  # pragma: nocover
    return auth_data.token


@router.get("/userinfo", response_model=UserDTO, status_code=status.HTTP_200_OK)
def me(user: UserDep) -> Any:
    return user


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout() -> Any:
    response = Response()
    response = cookie_transport.delete_token(response)
    return vt_transport.delete_token(response)
