from typing import Any

import humanize
from sqladmin import ModelView

from app.apps.models import App
from app.base.types import naive_utc
from app.db.models import OAuthAccount, User


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


class UserAdmin(BaseView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

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


class OAuthClientAdmin(BaseView, model=App):
    name = "App"
    name_plural = "Apps"
    icon = "fa-solid fa-cube"

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


class OAuthAccountAdmin(BaseView, model=OAuthAccount):
    name = "OAuth Account"
    name_plural = "OAuth Accounts"
    icon = "fa-brands fa-google"

    column_list = [
        OAuthAccount.id,
        OAuthAccount.user_id,
        OAuthAccount.provider,
        OAuthAccount.email,
        OAuthAccount.display_name,
        OAuthAccount.created_at,
        OAuthAccount.updated_at,
    ]

    column_searchable_list = [
        OAuthAccount.email,
    ]
