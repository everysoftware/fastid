# Import models for alembic
from sqlalchemy.orm import configure_mappers

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.database.base import BaseOrm
from fastid.notify.models import EmailTemplate, Notification, TelegramTemplate
from fastid.oauth.models import OAuthAccount, OAuthProvider
from fastid.webhooks.models import WebhookAttempt, WebhookDelivery, WebhookEndpoint

configure_mappers()


from fastid.database.versioning import (  # noqa: E402
    AppVersion,
    EmailTemplateVersion,
    OAuthAccountVersion,
    OAuthProviderVersion,
    TelegramTemplateVersion,
    Transaction,
    UserVersion,
    WebhookEndpointVersion,
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
    "WebhookEndpointVersion",
    "WebhookEndpoint",
    "WebhookAttempt",
    "WebhookDelivery",
    "OAuthAccountVersion",
    "OAuthProviderVersion",
]
