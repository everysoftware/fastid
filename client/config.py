from app.base.schemas import BaseSettings


class Settings(BaseSettings):
    client_id: str = "test"
    client_secret: str = "test"


settings = Settings()
