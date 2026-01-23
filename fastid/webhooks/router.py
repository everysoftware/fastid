from fastapi import APIRouter

from fastid.webhooks.schemas import UserWebhook

router = APIRouter()


@router.post("user-registration")
def user_registration(body: UserWebhook) -> None:
    pass


@router.post("user-login")
def user_login(body: UserWebhook) -> None:
    pass


@router.post("user-delete")
def user_delete(body: UserWebhook) -> None:
    pass


@router.post("user-update-profile")
def user_update_profile(body: UserWebhook) -> None:
    pass


@router.post("user-change-email")
def user_change_email(body: UserWebhook) -> None:
    pass


@router.post("user-change-password")
def user_change_password(body: UserWebhook) -> None:
    pass
