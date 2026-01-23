from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter, OperationColumnFilter

from fastid.admin.views.base import BaseView
from fastid.database.models import Notification, OAuthAccount, User


class UserAdmin(BaseView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    category = "Entities"
    category_icon = "fa-solid fa-cloud"

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

    column_filters = [
        BooleanFilter(User.is_active),
        BooleanFilter(User.is_verified),
        BooleanFilter(User.is_superuser),
        OperationColumnFilter(User.email),
        OperationColumnFilter(User.first_name),
        OperationColumnFilter(User.last_name),
    ]


class OAuthAccountAdmin(BaseView, model=OAuthAccount):
    name = "OAuth Account"
    name_plural = "OAuth Accounts"
    icon = "fa-brands fa-google"
    category = "Entities"

    column_list = [
        OAuthAccount.id,
        OAuthAccount.user,
        OAuthAccount.provider,
        OAuthAccount.email,
        OAuthAccount.display_name,
        OAuthAccount.created_at,
        OAuthAccount.updated_at,
    ]
    column_filters = [
        AllUniqueStringValuesFilter(OAuthAccount.provider),
        OperationColumnFilter(OAuthAccount.user_id),
        OperationColumnFilter(OAuthAccount.email),
    ]


class NotificationAdmin(BaseView, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    category = "Entities"

    column_list = [
        Notification.id,
        Notification.user,
        Notification.type,
        Notification.template,
        Notification.created_at,
        Notification.updated_at,
    ]
    column_filters = [
        AllUniqueStringValuesFilter(Notification.type),
        OperationColumnFilter(Notification.user_id),
        OperationColumnFilter(Notification.template),
    ]
