from typing import Any

import humanize
from sqladmin import ModelView

from fastid.apps.models import App
from fastid.database.alembic import OAuthAccount, User
from fastid.database.utils import naive_utc
from fastid.database.versioning import AppVersion, EmailTemplateVersion, TelegramTemplateVersion, UserVersion
from fastid.notify.models import EmailTemplate, Notification, TelegramTemplate


def time_format(m: Any, a: Any) -> Any:
    return humanize.naturaltime(getattr(m, a), when=naive_utc())


class BaseView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True

    column_sortable_list = [
        "created_at",
        "updated_at",
    ]

    column_default_sort = [("created_at", True)]
    column_formatters = {
        "created_at": time_format,
        "updated_at": time_format,
    }
    column_exclude_list = ["versions"]
    column_details_exclude_list = ["versions"]


# Users


class UserAdmin(BaseView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "Users"

    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.is_active,
        User.is_superuser,
        User.is_verified,
        User.created_at,
        User.updated_at,
    ]

    column_searchable_list = [
        User.email,
    ]


class OAuthAccountAdmin(BaseView, model=OAuthAccount):
    name = "OAuth Account"
    name_plural = "OAuth Accounts"
    icon = "fa-brands fa-google"
    category = "Users"

    column_list = [
        OAuthAccount.id,
        OAuthAccount.user,
        OAuthAccount.provider,
        OAuthAccount.email,
        OAuthAccount.display_name,
        OAuthAccount.created_at,
        OAuthAccount.updated_at,
    ]

    column_searchable_list = [
        OAuthAccount.email,
    ]


class NotificationAdmin(BaseView, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    category = "Users"

    column_list = [
        Notification.id,
        Notification.user,
        Notification.type,
        Notification.template,
        Notification.created_at,
        Notification.updated_at,
    ]

    column_searchable_list = [
        Notification.user,
    ]


# Settings


class AppAdmin(BaseView, model=App):
    name = "App"
    name_plural = "Apps"
    icon = "fa-solid fa-cube"
    category = "Settings"
    category_icon = "fa-solid fa-cog"

    column_list = [
        App.id,
        App.name,
        App.is_active,
        App.created_at,
        App.updated_at,
    ]

    column_searchable_list = [
        App.name,
    ]


class EmailTemplateAdmin(BaseView, model=EmailTemplate):
    name = "Email Template"
    name_plural = "Email Templates"
    icon = "fa-solid fa-envelope"
    category = "Settings"
    category_icon = "fa-solid fa-cog"

    column_list = [
        EmailTemplate.id,
        EmailTemplate.slug,
        EmailTemplate.subject,
        EmailTemplate.created_at,
        EmailTemplate.updated_at,
    ]

    column_searchable_list = [
        EmailTemplate.slug,
    ]


class TelegramTemplateAdmin(BaseView, model=TelegramTemplate):
    name = "Telegram Template"
    name_plural = "Telegram Templates"
    icon = "fa-brands fa-telegram"
    category = "Settings"
    category_icon = "fa-solid fa-cog"

    column_list = [
        TelegramTemplate.id,
        TelegramTemplate.slug,
        TelegramTemplate.created_at,
        TelegramTemplate.updated_at,
    ]

    column_searchable_list = [
        TelegramTemplate.slug,
    ]


# Versioning


class BaseVersionView(BaseView):
    can_create = False
    can_edit = False
    can_delete = False

    icon = "fa-solid fa-code-fork"
    category = "Versioning"


class UserVersionAdmin(BaseVersionView, model=UserVersion):
    name = "User Version"
    name_plural = "User Versions"

    column_list = [
        UserVersion.id,
        UserVersion.email,
        UserVersion.first_name,
        UserVersion.is_active,
        UserVersion.is_superuser,
        UserVersion.is_verified,
        UserVersion.created_at,
        UserVersion.updated_at,
    ]

    column_searchable_list = [
        UserVersion.email,
    ]


class AppVersionAdmin(BaseVersionView, model=AppVersion):
    name = "App Version"
    name_plural = "App Versions"

    column_list = [
        AppVersion.id,
        AppVersion.name,
        AppVersion.is_active,
        AppVersion.created_at,
        AppVersion.updated_at,
    ]

    column_searchable_list = [
        AppVersion.name,
    ]


class EmailTemplateVersionAdmin(BaseVersionView, model=EmailTemplateVersion):
    name = "Email Template Version"
    name_plural = "Email Template Versions"

    column_list = [
        EmailTemplateVersion.id,
        EmailTemplateVersion.slug,
        EmailTemplateVersion.subject,
        EmailTemplateVersion.created_at,
        EmailTemplateVersion.updated_at,
    ]

    column_searchable_list = [
        EmailTemplateVersion.slug,
    ]


class TelegramTemplateVersionAdmin(BaseVersionView, model=TelegramTemplateVersion):
    name = "Telegram Template Version"
    name_plural = "Telegram Template Versions"

    column_list = [
        TelegramTemplateVersion.id,
        TelegramTemplateVersion.slug,
        TelegramTemplateVersion.created_at,
        TelegramTemplateVersion.updated_at,
    ]

    column_searchable_list = [
        TelegramTemplateVersion.slug,
    ]
