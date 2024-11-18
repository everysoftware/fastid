import datetime
from abc import ABC, abstractmethod
from typing import Any, Mapping, cast
from typing import MutableMapping

import jwt
from jwt import InvalidTokenError

from app.authlib.exceptions import InvalidToken, InvalidTokenType
from app.authlib.schemas import (
    TokenResponse,
    TypeParams,
    AccessTokenClaims,
    RefreshTokenClaims,
    IDTokenClaims,
)

type Subject = Any


class ITokenBackend(ABC):
    @abstractmethod
    def create_at(
        self, sub: Subject, scope: str | None = None, **kwargs: Any
    ) -> str: ...

    @abstractmethod
    def create_rt(
        self, sub: Subject, scope: str | None = None, **kwargs: Any
    ) -> str: ...

    @abstractmethod
    def create_it(
        self,
        sub: Subject,
        *,
        name: str | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        email: str | None = None,
        email_verified: bool | None = None,
        **kwargs: Any,
    ) -> str: ...

    @abstractmethod
    def to_response(
        self,
        at: str | None = None,
        rt: str | None = None,
        it: str | None = None,
    ) -> TokenResponse: ...

    @abstractmethod
    def validate_at(self, token: str) -> AccessTokenClaims: ...

    @abstractmethod
    def validate_rt(self, token: str) -> RefreshTokenClaims: ...

    @abstractmethod
    def validate_it(self, token: str) -> IDTokenClaims: ...


class BackendConfig:
    def __init__(self) -> None:
        self.types: MutableMapping[str, TypeParams] = {}

    def add_type(self, token_type: str, params: TypeParams) -> None:
        self.types[token_type] = params

    def get_type(self, token_type: str) -> TypeParams:
        return self.types[token_type]

    def has_type(self, token_type: str) -> bool:
        return token_type in self.types

    def get_lifetime(self, token_type: str) -> int | None:
        expires_in = self.types[token_type].expires_in
        if expires_in is None:
            return None
        return int(expires_in.total_seconds())


class TokenBackend(ITokenBackend):
    def __init__(self, config: BackendConfig) -> None:
        self.config = config

    def create_at(
        self, sub: Subject, scope: str | None = None, **kwargs: Any
    ) -> str:
        return self._create(
            "access",
            {
                "sub": str(sub),
                "scope": scope,
                **kwargs,
            },
        )

    def create_rt(
        self, sub: Subject, scope: str | None = None, **kwargs: Any
    ) -> str:
        return self._create(
            "refresh",
            {
                "sub": str(sub),
                "scope": scope,
                **kwargs,
            },
        )

    def create_it(
        self,
        sub: Subject,
        *,
        name: str | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        email: str | None = None,
        email_verified: bool | None = None,
        **kwargs: Any,
    ) -> str:
        return self._create(
            "id",
            {
                "sub": str(sub),
                "name": name,
                "given_name": given_name,
                "family_name": family_name,
                "email": email,
                "email_verified": email_verified,
                **kwargs,
            },
        )

    def to_response(
        self,
        at: str | None = None,
        rt: str | None = None,
        it: str | None = None,
    ) -> TokenResponse:
        if rt is None:
            expires_in = self.config.get_lifetime("access")
        else:
            expires_in = self.config.get_lifetime("refresh")
        return TokenResponse(
            access_token=at,
            refresh_token=rt,
            id_token=it,
            expires_in=expires_in,
        )

    def validate_at(self, token: str) -> AccessTokenClaims:
        claims = self._validate("access", token)
        return AccessTokenClaims.model_validate(claims)

    def validate_rt(self, token: str) -> RefreshTokenClaims:
        claims = self._validate("refresh", token)
        return RefreshTokenClaims.model_validate(claims)

    def validate_it(self, token: str) -> IDTokenClaims:
        claims = self._validate("id", token)
        return IDTokenClaims.model_validate(claims)

    def _create(self, token_type: str, payload: Mapping[str, Any]) -> str:
        params = self.config.get_type(token_type)
        now = datetime.datetime.now(datetime.UTC)
        claims = dict(
            iss=params.issuer,
            typ=token_type,
            iat=now,
            **payload,
        )
        if params.expires_in is not None:
            claims["exp"] = now + params.expires_in
        return jwt.encode(
            claims,
            params.private_key,
            algorithm=params.algorithm,
        )

    def _validate(
        self, token_type: str, token: str, aud: str | None = None
    ) -> Mapping[str, Any]:
        params = self.config.get_type(token_type)
        try:
            decoded = jwt.decode(
                token,
                params.public_key,
                algorithms=[params.algorithm],
                issuer=params.issuer,
                audience=aud,
            )
        except InvalidTokenError as e:
            raise InvalidToken() from e
        if decoded["typ"] != token_type:
            raise InvalidTokenType()
        return cast(Mapping[str, Any], decoded)
