from fastid.core.schemas import BaseSettings


class Settings(BaseSettings):
    fastid_url: str = "http://localhost:8012"
    client_id: str
    client_secret: str


settings = Settings()
