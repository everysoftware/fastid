from sqladmin.authentication import AuthenticationBackend
from starlette import status
from starlette.requests import Request

from app.runner.testing import api_client


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        form = {
            "grant_type": "password",
            "username": data["username"],
            "password": data["password"],
            "scope": "admin",
        }
        response = api_client.post(
            "/api/v1/auth/token",
            data=form,  # type: ignore[arg-type]
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != status.HTTP_200_OK:
            return False
        token = response.json()
        request.session.update({"token": token["access_token"]})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        response = api_client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != status.HTTP_200_OK:
            return False
        user = response.json()
        if not user["is_superuser"]:
            return False
        return True


admin_auth = AdminAuth(secret_key="...")
