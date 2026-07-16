# Import models for alembic
from sqlalchemy.orm import configure_mappers

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.database.base import BaseOrm
from fastid.notify.models import EmailTemplate, Notification, TelegramTemplate
from fastid.oauth.models import OAuthAccount, OAuthProvider
from fastid.webhooks.models import Webhook, WebhookEvent

configure_mappers()


from fastid.database.versioning import (  # noqa: E402
    AppVersion,
    EmailTemplateVersion,
    OAuthAccountVersion,
    OAuthProviderVersion,
    TelegramTemplateVersion,
    Transaction,
    UserVersion,
    WebhookVersion,
)

__all__ = [
    "App",
    "BaseOrm",
    "OAuthAccount",
    "OAuthProvider",
    "User",
    "EmailTemplate",
    "TelegramTemplate",
    "Notification",
    "UserVersion",
    "AppVersion",
    "EmailTemplateVersion",
    "TelegramTemplateVersion",
    "Transaction",
    "WebhookVersion",
    "Webhook",
    "WebhookEvent",
    "OAuthAccountVersion",
    "OAuthProviderVersion",
]
