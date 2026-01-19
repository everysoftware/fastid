import secrets

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from fastid.admin.config import admin_settings
from fastid.auth.config import auth_settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        username = data["username"]
        password = data["password"]
        assert isinstance(username, str)
        assert isinstance(password, str)

        if not secrets.compare_digest(username, admin_settings.email) or not secrets.compare_digest(
            password,
            admin_settings.password,
        ):
            return False
        request.session.update({"authenticated": True})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("authenticated"))


admin_auth = AdminAuth(secret_key=auth_settings.jwt_private_key.read_text())
