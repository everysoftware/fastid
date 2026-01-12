from fastid.core.schemas import BaseSettings


class Settings(BaseSettings):
    fastid_url: str = "http://localhost:8012"
    fastid_client_id: str
    fastid_client_secret: str


settings = Settings()
