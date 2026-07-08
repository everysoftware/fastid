from fastid.core.schemas import BaseSettings


class Settings(BaseSettings):
    url: str = "http://localhost:8012"
    client_id: str
    client_secret: str


settings = Settings()
