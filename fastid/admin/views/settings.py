from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter, OperationColumnFilter

from fastid.admin.views.base import BaseView
from fastid.admin.views.utils import json_format
from fastid.database.models import App, EmailTemplate, OAuthProvider, TelegramTemplate, Webhook, WebhookEvent


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
        OperationColumnFilter(App.redirect_uris),
    ]


class OAuthProviderAdmin(BaseView, model=OAuthProvider):
    can_create = False
    can_delete = False

    name = "OAuth Provider"
    name_plural = "OAuth Providers"
    icon = "fa-solid fa-right-to-bracket"
    category = "Settings"

    column_list = [
        OAuthProvider.id,
        OAuthProvider.name,
        OAuthProvider.enabled,
        OAuthProvider.client_id,
        OAuthProvider.created_at,
        OAuthProvider.updated_at,
    ]
    column_filters = [
        BooleanFilter(OAuthProvider.enabled),
        AllUniqueStringValuesFilter(OAuthProvider.name),
    ]
    form_columns = [
        OAuthProvider.enabled,
        OAuthProvider.client_id,
        OAuthProvider.client_secret,
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


class WebhookAdmin(BaseView, model=Webhook):
    name = "Webhook"
    name_plural = "Webhooks"
    icon = "fa-solid fa-globe"
    category = "Settings"

    column_list = [
        Webhook.id,
        Webhook.app,
        Webhook.url,
        Webhook.created_at,
        Webhook.updated_at,
    ]
    column_filters = [
        OperationColumnFilter(Webhook.app_id),
        AllUniqueStringValuesFilter(Webhook.type),
        OperationColumnFilter(Webhook.url),
    ]


class WebhookEventAdmin(BaseView, model=WebhookEvent):
    can_create = False
    can_edit = False
    can_delete = False

    name = "Webhook Event"
    name_plural = "Webhook Events"
    icon = "fa-solid fa-book-atlas"
    category = "Settings"

    column_list = [
        WebhookEvent.id,
        WebhookEvent.webhook,
        "webhook.type",
        WebhookEvent.status_code,
        WebhookEvent.request,
        WebhookEvent.response,
        WebhookEvent.created_at,
        WebhookEvent.updated_at,
    ]
    column_filters = [
        OperationColumnFilter(WebhookEvent.webhook_id),
        OperationColumnFilter(WebhookEvent.status_code),
    ]
    column_formatters = {WebhookEvent.response: json_format, WebhookEvent.request: json_format}
