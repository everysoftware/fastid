from pydantic_settings import SettingsConfigDict

from app.domain.schemas import BaseSettings


class OAuthSettings(BaseSettings):
    name: str = "Frontend"
    id: str = "frontend"
    secret: str = "changethis"
    primary_url: str = "http://localhost:8000"
    redirect_uris: list[str] = ["http://localhost:8000"]

    model_config = SettingsConfigDict(env_prefix="oauth_client_")
