import datetime
from abc import ABC, abstractmethod
from typing import Mapping, Any

import jwt
from jwt import InvalidTokenError

from app.auth.exceptions import InvalidToken, InvalidTokenType
from app.authlib.schemas import TokenConfig, JWTClaims


class ITokenManager(ABC):
    tokens: Mapping[str, TokenConfig]

    @abstractmethod
    def create(self, token_type: str, payload: Mapping[str, Any]) -> str: ...

    @abstractmethod
    def get_lifetime(self, token_type: str) -> int: ...

    @abstractmethod
    def validate(self, token_type: str, token: str) -> JWTClaims: ...


class TokenManager(ITokenManager):
    def __init__(self, *tokens: TokenConfig):
        self.tokens = {params.type: params for params in tokens}

    def create(self, token_type: str, payload: Mapping[str, Any]) -> str:
        params = self.tokens[token_type]
        now = datetime.datetime.now(datetime.UTC)
        claims = JWTClaims(
            iss=params.issuer,
            aud=params.audience,
            typ=params.type,
            iat=now,
            nbf=now,
            exp=now + params.expires_in,
            **payload,
        )
        return jwt.encode(
            claims.model_dump(
                mode="json",
                exclude_none=True,
                include=params.include,
                exclude=params.exclude,
            ),
            params.private_key,
            algorithm=params.algorithm,
        )

    def get_lifetime(self, token_type: str) -> int:
        return int(self.tokens[token_type].expires_in.total_seconds())

    def validate(self, token_type: str, token: str) -> JWTClaims:
        params = self.tokens[token_type]
        try:
            decoded = jwt.decode(
                token,
                params.public_key,
                algorithms=[params.algorithm],
                issuer=params.issuer,
                audience=params.audience,
            )
            payload = JWTClaims.model_validate(decoded)
        except InvalidTokenError as e:
            raise InvalidToken() from e
        if payload.typ != token_type:
            raise InvalidTokenType()
        return payload
