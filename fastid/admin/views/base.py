from sqladmin import ModelView

from fastid.admin.views.utils import time_format


class BaseView(ModelView):
    column_sortable_list = [
        "created_at",
        "updated_at",
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    column_formatters = {
        "created_at": time_format,
        "updated_at": time_format,
    }
    column_exclude_list = ["versions"]
    column_details_exclude_list = ["versions"]
    form_excluded_columns = ["versions"]
