from typing import Literal

from app.base.schemas import BaseModel
from app.base.types import UUID

NotifyMethod = Literal["telegram", "email"]


class NotifyResponse(BaseModel):
    user_id: UUID
    status: str
    method: NotifyMethod
