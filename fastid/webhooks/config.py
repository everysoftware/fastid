from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings
from fastid.webhooks.schemas import SignatureAlgorithm


class WebhookSettings(BaseSettings):
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.sha256
    signature_header: str = "X-Webhook-Signature"
    timestamp_header: str = "X-Webhook-Timestamp"
    id_header: str = "X-Webhook-Id"
    tolerance_seconds: int = 300
    page_expires_in_seconds: int = 60

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}webhook_")


webhook_settings = WebhookSettings()
