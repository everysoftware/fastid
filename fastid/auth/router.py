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
    webhook = SendWebhookRequest(
        type=WebhookType.user_registration, payload=UserDTO.model_validate(user).model_dump(mode="json")
    )
    background.add_task(webhooks.send, webhook)  # pragma: nocover
    return user  # pragma: nocover


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
    background: BackgroundTasks,
) -> Any:
    match form.grant_type:
        case OAuth2Grant.password:
            response = await password_grant.authorize(OAuth2PasswordRequest.model_validate(form))
        case OAuth2Grant.authorization_code:
            response = await authorization_code_grant.authorize(OAuth2AuthorizationCodeRequest.model_validate(form))
        case OAuth2Grant.refresh_token:
            response = await refresh_token_grant.authorize(OAuth2RefreshTokenRequest.model_validate(form))
        case OAuth2Grant.client_credentials:
            response = await client_credentials_grant.authorize(OAuth2ClientCredentialsRequest.model_validate(form))
        case _:
            raise NotSupportedGrantError
    if response.sub_type == SubscriberType.user and response.user is not None:
        webhook = SendWebhookRequest(
            type=WebhookType.user_login, payload={"user": response.user.model_dump(mode="json")}
        )
        background.add_task(webhooks.send, webhook)  # pragma: nocover
    return cookie_transport.get_login_response(response.token)


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
