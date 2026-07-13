import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from fastid.auth.config import auth_settings
from fastid.auth.schemas import JWK, JWKS, DiscoveryDocument
from fastid.core.config import core_settings
from fastid.core.urls import join_url_path
from fastid.security.schemas import JWTPayload


def get_discovery_document(server_url: str) -> DiscoveryDocument:
    return DiscoveryDocument(
        issuer=server_url,
        authorization_endpoint=f"{server_url}{join_url_path(core_settings.frontend_path, 'authorize')}",
        token_endpoint=f"{server_url}{join_url_path(core_settings.api_path, 'token')}",
        userinfo_endpoint=f"{server_url}{join_url_path(core_settings.api_path, 'userinfo')}",
        jwks_uri=f"{server_url}{join_url_path(core_settings.frontend_path, '.well-known/jwks.json')}",
        scopes_supported=["openid", "email", "name", "offline_access"],
        response_types_supported=["code"],
        grant_types_supported=["authorization_code", "refresh_token"],
        subject_types_supported=["public"],
        id_token_signing_alg_values_supported=["RS256"],
        claims_supported=list(JWTPayload.model_fields),
    )


def get_jwks() -> JWKS:
    public_key = serialization.load_pem_public_key(auth_settings.jwt_public_key.read_bytes())
    assert isinstance(public_key, rsa.RSAPublicKey)
    public_numbers = public_key.public_numbers()
    n = public_numbers.n
    e = public_numbers.e
    key = JWK(
        kty="RSA",
        use="sig",
        alg="RS256",
        kid="primary",
        n=base64.urlsafe_b64encode(n.to_bytes((n.bit_length() + 7) // 8, "big")).decode("utf-8").rstrip("="),
        e=base64.urlsafe_b64encode(e.to_bytes((e.bit_length() + 7) // 8, "big")).decode("utf-8").rstrip("="),
    )
    return JWKS(keys=[key])


jwks = get_jwks()
