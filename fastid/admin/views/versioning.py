from sqladmin import ModelView
from sqladmin.filters import OperationColumnFilter

from fastid.admin.views.utils import operation_type_format, time_format
from fastid.database.versioning import (
    AppVersion,
    EmailTemplateVersion,
    TelegramTemplateVersion,
    Transaction,
    UserVersion,
    WebhookVersion,
)


class TransactionAdmin(ModelView, model=Transaction):
    can_create = False
    can_edit = False
    can_delete = False

    name = "Transaction"
    name_plural = "Transactions"
    icon = "fa-solid fa-code-pull-request"
    category = "Versioning"
    category_icon = "fa-solid fa-code-fork"

    column_formatters = {
        "issued_at": time_format,
    }
    column_list = [
        Transaction.id,
        Transaction.user,
        Transaction.remote_addr,
        Transaction.issued_at,
    ]
    column_searchable_list = [
        Transaction.id,
    ]
    column_default_sort = [("issued_at", True)]
    column_sortable_list = ["issued_at"]


class BaseVersionView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False

    icon = "fa-solid fa-code-commit"
    category = "Versioning"

    column_list = ["transaction_id", "id", "operation_type", "transaction.issued_at"]
    column_default_sort = [("transaction_id", True)]
    column_searchable_list = ["id"]
    column_formatters = {"transaction.issued_at": time_format, "operation_type": operation_type_format}
    column_exclude_list = ["transaction"]
    column_details_exclude_list = ["transaction"]
    form_excluded_columns = ["transaction"]
    column_sortable_list = ["transaction_id"]
    column_filters = [
        OperationColumnFilter("transaction_id"),
        OperationColumnFilter("operation_type"),
    ]


class UserVersionAdmin(BaseVersionView, model=UserVersion):
    name = "User Version"
    name_plural = "User Versions"


class AppVersionAdmin(BaseVersionView, model=AppVersion):
    name = "App Version"
    name_plural = "App Versions"


class EmailTemplateVersionAdmin(BaseVersionView, model=EmailTemplateVersion):
    name = "Email Template Version"
    name_plural = "Email Template Versions"


class TelegramTemplateVersionAdmin(BaseVersionView, model=TelegramTemplateVersion):
    name = "Telegram Template Version"
    name_plural = "Telegram Template Versions"


class WebhookVersionAdmin(BaseVersionView, model=WebhookVersion):
    name = "Webhook Version"
    name_plural = "Webhook Versions"
