from typing import Any

import humanize
from sqladmin import ModelView

from app.db import OAuthAccountOrm, UserOrm
from app.domain.types import naive_utc
from app.apps.models import AppOrm


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


class UserAdmin(BaseView, model=UserOrm):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        UserOrm.id,
        UserOrm.email,
        UserOrm.first_name,
        UserOrm.is_active,
        UserOrm.is_superuser,
        UserOrm.is_verified,
        UserOrm.created_at,
        UserOrm.updated_at,
    ]

    column_searchable_list = [
        UserOrm.email,
    ]


class OAuthClientAdmin(BaseView, model=AppOrm):
    name = "OAuth Client"
    name_plural = "OAuth Clients"
    icon = "fa-solid fa-cube"

    column_list = [
        AppOrm.id,
        AppOrm.name,
        AppOrm.is_active,
        AppOrm.created_at,
        AppOrm.updated_at,
    ]

    column_searchable_list = [
        AppOrm.name,
    ]


class OAuthAccountAdmin(BaseView, model=OAuthAccountOrm):
    name = "OAuth Account"
    name_plural = "OAuth Accounts"
    icon = "fa-brands fa-google"

    column_list = [
        OAuthAccountOrm.id,
        OAuthAccountOrm.user_id,
        OAuthAccountOrm.provider,
        OAuthAccountOrm.email,
        OAuthAccountOrm.display_name,
        OAuthAccountOrm.created_at,
        OAuthAccountOrm.updated_at,
    ]

    column_searchable_list = [
        UserOrm.email,
    ]
