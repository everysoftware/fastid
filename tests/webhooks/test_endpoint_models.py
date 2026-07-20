from fastid.apps.models import App
from fastid.webhooks.models import WebhookDelivery, WebhookEndpoint


def test_webhook_endpoint_and_delivery_mapping_names() -> None:
    assert WebhookEndpoint.__tablename__ == "webhook_endpoints"
    assert WebhookDelivery.__table__.c.endpoint_id.name == "endpoint_id"
    foreign_key = next(iter(WebhookDelivery.__table__.c.endpoint_id.foreign_keys))
    assert foreign_key.target_fullname == "webhook_endpoints.id"
    assert WebhookDelivery.endpoint.property.mapper.class_ is WebhookEndpoint
    assert App.webhook_endpoints.property.mapper.class_ is WebhookEndpoint
