from app.base.schemas import BaseSettings


class Settings(BaseSettings):
    fastid_url: str = "http://localhost:8012"
    client_id: str = "019382ce69c278428e3fd22bc1433b9e"
    client_secret: str = "019382ce69c278428e3fd234fa7a672d"


settings = Settings()
