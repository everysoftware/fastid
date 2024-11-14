from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.api.exceptions import ClientError
from app.auth.schemas import OAuth2TokenRequest
from app.auth.service import AuthUseCases
from app.authlib.oauth import OAuth2Grant
from app.db.connection import session_factory
from app.db.uow import AlchemyUOW


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        form = OAuth2TokenRequest(
            grant_type=OAuth2Grant.password,
            username=data["username"],
            password=data["password"],
            scope="admin",
        )
        async with AlchemyUOW(session_factory) as uow:
            auth = AuthUseCases(uow)
            try:
                token = await auth.authorize(form)
            except ClientError:
                return False
        request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        async with AlchemyUOW(session_factory) as uow:
            auth = AuthUseCases(uow)
            try:
                user = await auth.get_userinfo(token)
            except ClientError:
                return False

        if not user.is_superuser:
            return False

        return True


admin_auth = AdminAuth(secret_key="...")
