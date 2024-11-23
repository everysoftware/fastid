from app.base.schemas import BaseModel


class OTPRequest(BaseModel):
    new_email: str | None = None


class VerifyTokenRequest(BaseModel):
    code: str
