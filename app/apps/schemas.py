from app.base.schemas import BaseModel, EntityDTO


class AppBase(BaseModel):
    name: str
    slug: str
    redirect_uris: str
    is_active: bool = True


class AppDTO(EntityDTO, AppBase):
    client_id: str
    client_secret: str


class AppCreate(AppBase):
    client_id: str | None = None
    client_secret: str | None = None
