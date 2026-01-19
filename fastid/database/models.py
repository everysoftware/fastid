# Import models for alembic
from sqlalchemy.orm import configure_mappers

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.database.base import BaseOrm
from fastid.notify.models import EmailTemplate, Notification, TelegramTemplate
from fastid.oauth.models import OAuthAccount

configure_mappers()


from fastid.database.versioning import (  # noqa: E402
    AppVersion,
    EmailTemplateVersion,
    TelegramTemplateVersion,
    Transaction,
    UserVersion,
)

__all__ = [
    "App",
    "BaseOrm",
    "OAuthAccount",
    "User",
    "EmailTemplate",
    "TelegramTemplate",
    "Notification",
    "UserVersion",
    "AppVersion",
    "EmailTemplateVersion",
    "TelegramTemplateVersion",
    "Transaction",
]
