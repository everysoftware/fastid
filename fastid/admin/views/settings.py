from sqladmin.filters import BooleanFilter, OperationColumnFilter

from fastid.admin.views.base import BaseView
from fastid.database.models import App, EmailTemplate, TelegramTemplate


class AppAdmin(BaseView, model=App):
    name = "App"
    name_plural = "Apps"
    icon = "fa-solid fa-cube"
    category = "Settings"
    category_icon = "fa-solid fa-star"

    column_list = [
        App.id,
        App.name,
        App.is_active,
        App.created_at,
        App.updated_at,
    ]
    column_filters = [
        BooleanFilter(App.is_active),
        OperationColumnFilter(App.client_id),
    ]


class EmailTemplateAdmin(BaseView, model=EmailTemplate):
    name = "Email Template"
    name_plural = "Email Templates"
    icon = "fa-solid fa-envelope"
    category = "Settings"

    column_list = [
        EmailTemplate.id,
        EmailTemplate.slug,
        EmailTemplate.subject,
        EmailTemplate.created_at,
        EmailTemplate.updated_at,
    ]
    column_filters = [
        OperationColumnFilter(EmailTemplate.slug),
    ]


class TelegramTemplateAdmin(BaseView, model=TelegramTemplate):
    name = "Telegram Template"
    name_plural = "Telegram Templates"
    icon = "fa-brands fa-telegram"
    category = "Settings"

    column_list = [
        TelegramTemplate.id,
        TelegramTemplate.slug,
        TelegramTemplate.created_at,
        TelegramTemplate.updated_at,
    ]
    column_filters = [
        OperationColumnFilter(EmailTemplate.slug),
    ]
