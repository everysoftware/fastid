from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Form, status
from starlette.responses import Response

from fastid.auth.dependencies import AuthDep, UserDep, cookie_transport, vt_transport
from fastid.auth.exceptions import NotSupportedGrantError
from fastid.auth.grants import (
    AuthorizationCodeGrant,
    ClientCredentialsGrant,
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
from fastid.notify.dependencies import NotifyDep
from fastid.notify.schemas import PushNotificationRequest
from fastid.webhooks.dependencies import WebhooksDep
from fastid.webhooks.models import WebhookType
from fastid.webhooks.schemas import SendWebhookRequest

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
    user_data = UserDTO.model_validate(user).model_dump(mode="json")
    webhook = SendWebhookRequest(type=WebhookType.user_registration, payload=user_data | {"user": user_data})
    await webhooks.enqueue(webhook)
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
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            auth_data = await password_grant.authorize(OAuth2PasswordRequest.model_validate(form))
        case _:
            raise NotSupportedGrantError
    assert auth_data.user is not None
    webhook = SendWebhookRequest(type=WebhookType.user_login, payload={"user": auth_data.user.model_dump(mode="json")})
    await webhooks.enqueue(webhook)
    return cookie_transport.get_login_response(auth_data.token)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def authorize(  # noqa: PLR0913
    form: Annotated[OAuth2TokenRequest, Form()],
    password_grant: Annotated[PasswordGrant, Depends()],
    authorization_code_grant: Annotated[AuthorizationCodeGrant, Depends()],
    refresh_token_grant: Annotated[RefreshTokenGrant, Depends()],
    client_credentials_grant: Annotated[ClientCredentialsGrant, Depends()],
    webhooks: WebhooksDep,
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            auth_data = await password_grant.authorize(OAuth2PasswordRequest.model_validate(form))
        case OAuth2Grant.authorization_code:
            auth_data = await authorization_code_grant.authorize(OAuth2AuthorizationCodeRequest.model_validate(form))
        case OAuth2Grant.refresh_token:
            auth_data = await refresh_token_grant.authorize(OAuth2RefreshTokenRequest.model_validate(form))
        case OAuth2Grant.client_credentials:
            auth_data = await client_credentials_grant.authorize(OAuth2ClientCredentialsRequest.model_validate(form))
        case _:
            raise NotSupportedGrantError
    if auth_data.sub_type == SubscriberType.user and auth_data.user is not None:
        webhook = SendWebhookRequest(
            type=WebhookType.user_login, payload={"user": auth_data.user.model_dump(mode="json")}
        )
        await webhooks.enqueue(webhook)
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
