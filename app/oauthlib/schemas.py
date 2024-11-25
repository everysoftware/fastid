from app.authlib.oauth import TokenResponse, OAuth2Callback
from app.base.schemas import BaseModel


class OpenID(BaseModel):
    id: str
    provider: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    picture: str | None = None


class TelegramCallback(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class OpenIDBearer(OpenID, TokenResponse):
    pass


UniversalCallback = OAuth2Callback | TelegramCallback
