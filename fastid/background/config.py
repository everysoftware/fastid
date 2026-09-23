from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class CPUWorkerSettings(BaseSettings):
    concurrency: int = 1
    batch_size: int = 1
    poll_seconds: float = 1.0
    lease_seconds: int = 60
    heartbeat_seconds: float = 15.0
    timeout_seconds: float = 300.0
    drain_timeout_seconds: float = 30.0
    retry_delays_seconds: tuple[int, ...] = (5, 30, 300)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}cpu_worker_")


cpu_worker_settings = CPUWorkerSettings()
