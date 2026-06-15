from collections.abc import Iterable
from pathlib import Path

from fastid.core.config import branding_settings
from fastid.notify.models import EmailTemplate, TelegramTemplate


def collect_email_templates() -> Iterable[EmailTemplate]:
    with Path("templates/notifications/html/base.html").open() as f:
        base = EmailTemplate(slug="base", subject="Base", source=f.read())
    with Path("templates/notifications/html/code.html").open() as f:
        code = EmailTemplate(slug="code", subject="Your verification code", source=f.read())
    with Path("templates/notifications/html/welcome.html").open() as f:
        welcome = EmailTemplate(slug="welcome", subject=f"Welcome to {branding_settings.title}", source=f.read())
    return [base, code, welcome]


def collect_telegram_templates() -> Iterable[TelegramTemplate]:
    with Path("templates/notifications/md/code.md").open() as f:
        code = TelegramTemplate(slug="code", source=f.read())
    with Path("templates/notifications/md/welcome.md").open() as f:
        welcome = TelegramTemplate(slug="welcome", source=f.read())
    return [code, welcome]
