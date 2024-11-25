from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.api.exceptions import ClientError
from app.auth.config import auth_settings
from app.auth.grants import PasswordGrant
from app.authlib.dependencies import token_backend
from app.authlib.oauth import OAuth2Grant, OAuth2PasswordRequest
from app.db.connection import session_factory
from app.db.uow import AlchemyUOW


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        form = OAuth2PasswordRequest(
            grant_type=OAuth2Grant.password,
            username=data["username"],
            password=data["password"],
            scope="admin",
        )
        async with AlchemyUOW(session_factory) as uow:
            grant = PasswordGrant(uow)
            try:
                token = await grant.authorize(form)
            except ClientError:
                return False
        request.session.update({"at": token.access_token})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("at")
        if not token:
            return False
        try:
            claims = token_backend.validate_at(token)
        except ClientError:
            return False
        if "admin" not in claims.scopes:
            return False
        return True


admin_auth = AdminAuth(secret_key=auth_settings.jwt_private_key.read_text())
