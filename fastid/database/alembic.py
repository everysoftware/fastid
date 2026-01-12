# Import models for alembic

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.database.base import BaseOrm
from fastid.notify.models import EmailTemplate, TelegramTemplate
from fastid.oauth.models import OAuthAccount

__all__ = ["App", "BaseOrm", "OAuthAccount", "User", "EmailTemplate", "TelegramTemplate"]
