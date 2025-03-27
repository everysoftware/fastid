import base64

from auth365.schemas import JWK, JWKS, DiscoveryDocument, JWTPayload
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth.config import auth_settings

discovery_document = DiscoveryDocument(
    issuer=auth_settings.issuer,
    authorization_endpoint=auth_settings.authorization_endpoint,
    token_endpoint=auth_settings.token_endpoint,
    userinfo_endpoint=auth_settings.userinfo_endpoint,
    jwks_uri=auth_settings.jwks_uri,
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
