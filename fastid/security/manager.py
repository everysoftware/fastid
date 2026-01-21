import datetime
from typing import TYPE_CHECKING, Any

import jwt
from jwt import InvalidTokenError as JWTInvalidTokenError

from fastid.security.exceptions import InvalidTokenTypeError, TokenError
from fastid.security.schemas import JWTConfig, JWTPayload

if TYPE_CHECKING:
    from collections.abc import MutableMapping


class JWTManager:
    def __init__(self, *config: JWTConfig) -> None:
        self.config: MutableMapping[str, JWTConfig] = {t.type: t for t in config}

    def create(self, token_type: str, payload: JWTPayload) -> tuple[str, dict[str, Any]]:
        config = self.config[token_type]
        now = datetime.datetime.now(datetime.UTC)
        claims = dict(
            iss=config.issuer,
            typ=token_type,
            iat=now,
            **payload.model_dump(exclude_none=True),
        )
        if config.expires_in is not None:
            claims["exp"] = now + config.expires_in
        assert config.private_key is not None
        token = jwt.encode(
            claims,
            config.private_key,
            algorithm=config.algorithm,
        )
        return token, claims

    def validate(
        self,
        token_type: str,
        token: str,
    ) -> JWTPayload:
        config = self.config[token_type]
        assert config.public_key is not None
        try:
            decoded = jwt.decode(
                token,
                config.public_key,
                algorithms=[config.algorithm],
                issuer=config.issuer,
            )
        except JWTInvalidTokenError as e:
            raise TokenError from e
        if decoded["typ"] != token_type:
            raise InvalidTokenTypeError
        return JWTPayload.model_validate(decoded)

    def get_lifetime(self, token_type: str) -> int | None:
        expires_in = self.config[token_type].expires_in
        if expires_in is None:
            return None
        return int(expires_in.total_seconds())
