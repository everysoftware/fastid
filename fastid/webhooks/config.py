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
    retry_delays_seconds: tuple[int, ...] = (0, 5, 300, 1800, 7200, 18000, 36000, 50400, 72000, 86400)
    retry_jitter_ratio: float = 0.2
    retry_after_max_seconds: int = 86400
    worker_batch_size: int = 100
    worker_concurrency: int = 20
    worker_poll_seconds: float = 1.0
    worker_lease_seconds: int = 60
    worker_metrics_port: int = 9101
    connect_timeout_seconds: float = 5.0
    read_timeout_seconds: float = 20.0
    write_timeout_seconds: float = 5.0
    pool_timeout_seconds: float = 5.0
    max_connections: int = 100
    max_keepalive_connections: int = 20
    max_response_bytes: int = 65536
    allow_insecure_urls: bool = False
    user_agent: str = "FastID-Webhooks/0.1"

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}webhook_")


webhook_settings = WebhookSettings()
