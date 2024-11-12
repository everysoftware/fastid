import uuid
from abc import ABC, abstractmethod

from app.authlib.schemas import JWTClaims, BearerToken
from app.authlib.tokens import ITokenManager
from app.auth.schemas import User


class IOAuth2Backend(ABC):
    @abstractmethod
    def create_access(self, user: User) -> str: ...

    @abstractmethod
    def create_refresh(self, user: User) -> str: ...

    @abstractmethod
    def create_bearer(
        self, user: User, *, refreshable: bool = False
    ) -> BearerToken: ...

    @abstractmethod
    def validate_access(self, token: str) -> JWTClaims: ...

    @abstractmethod
    def validate_refresh(self, token: str) -> JWTClaims: ...


class OAuth2Backend(IOAuth2Backend):
    def __init__(self, manager: ITokenManager) -> None:
        self.manager = manager

    def create_access(self, user: User) -> str:
        return self.manager.create(
            "access",
            {
                "sub": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        )

    def create_refresh(self, user: User) -> str:
        return self.manager.create(
            "refresh",
            {
                "sub": str(user.id),
            },
        )

    def create_bearer(
        self, user: User, *, refreshable: bool = False
    ) -> BearerToken:
        access_token = self.create_access(user)
        if refreshable:
            refresh_token = self.create_refresh(user)
            expires_in = self.manager.get_lifetime("refresh")
        else:
            refresh_token = None
            expires_in = self.manager.get_lifetime("access")
        return BearerToken(
            token_id=str(uuid.uuid4()),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    def validate_access(self, token: str) -> JWTClaims:
        return self.manager.validate("access", token)

    def validate_refresh(self, token: str) -> JWTClaims:
        return self.manager.validate("refresh", token)
