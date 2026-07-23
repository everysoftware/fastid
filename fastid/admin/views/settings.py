from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter, OperationColumnFilter

from fastid.admin.views.base import BaseView
from fastid.admin.views.utils import json_format
from fastid.database.models import (
    App,
    EmailTemplate,
    OAuthProvider,
    TelegramTemplate,
    WebhookAttempt,
    WebhookDelivery,
    WebhookEndpoint,
)


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


class WebhookEndpointAdmin(BaseView, model=WebhookEndpoint):
    name = "Webhook Endpoint"
    name_plural = "Webhook Endpoints"
    icon = "fa-solid fa-globe"
    category = "Settings"

    column_list = [
        WebhookEndpoint.id,
        WebhookEndpoint.app,
        WebhookEndpoint.url,
        WebhookEndpoint.is_active,
        WebhookEndpoint.disabled_reason,
        WebhookEndpoint.created_at,
        WebhookEndpoint.updated_at,
    ]
    column_filters = [
        OperationColumnFilter(WebhookEndpoint.app_id),
        AllUniqueStringValuesFilter(WebhookEndpoint.type),
        OperationColumnFilter(WebhookEndpoint.url),
        BooleanFilter(WebhookEndpoint.is_active),
    ]


class WebhookDeliveryAdmin(BaseView, model=WebhookDelivery):
    can_create = False
    can_edit = False
    can_delete = False

    name = "Webhook Delivery"
    name_plural = "Webhook Deliveries"
    icon = "fa-solid fa-book-atlas"
    category = "Settings"

    column_list = [
        WebhookDelivery.id,
        WebhookDelivery.event_id,
        WebhookDelivery.endpoint,
        "endpoint.type",
        WebhookDelivery.status,
        WebhookDelivery.attempt_count,
        WebhookDelivery.status_code,
        WebhookDelivery.response,
        WebhookDelivery.next_attempt_at,
        WebhookDelivery.completed_at,
        WebhookDelivery.created_at,
    ]
    column_filters = [
        OperationColumnFilter(WebhookDelivery.endpoint_id),
        OperationColumnFilter(WebhookDelivery.status_code),
        AllUniqueStringValuesFilter(WebhookDelivery.status),
    ]
    column_formatters = {WebhookDelivery.response: json_format, WebhookDelivery.request: json_format}


class WebhookAttemptAdmin(BaseView, model=WebhookAttempt):
    can_create = False
    can_edit = False
    can_delete = False

    name = "Webhook Attempt"
    name_plural = "Webhook Attempts"
    icon = "fa-solid fa-clock-rotate-left"
    category = "Settings"

    column_list = [
        WebhookAttempt.id,
        WebhookAttempt.delivery,
        WebhookAttempt.attempt_number,
        WebhookAttempt.status_code,
        WebhookAttempt.error,
        WebhookAttempt.duration_ms,
        WebhookAttempt.created_at,
    ]
    column_filters = [OperationColumnFilter(WebhookAttempt.delivery_id)]
    column_formatters = {WebhookAttempt.response: json_format, WebhookAttempt.request: json_format}
