# FastID

Customizable and ready-to-use identity server written in Python

![Sign In](assets/signin.png)

## Key features

* Complies with OpenID Connect
* Login via social networks. Support for Google, Telegram and Yandex at the moment
* One-time codes. Support for e-mail & telegram at the moment
* Admin panel to manage users & connected apps
* Module system to extend the functionality
* Metrics & tracing complied with OpenTelemetry
* Written in Python using FastAPI

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/everysoftware/fastid
    ```

2. Generate RSA keys:

    ```bash
    openssl genrsa -out certs/private.pem 2048
    openssl rsa -in certs/private.pem -pubout -out certs/public.pem
    ```

3. Create a `.env` file. Use the `.env.example` as a reference.
4. Run the application:

    ```bash
    make up
    ```

## Observability

**FastID** integrates perfectly with [this preset](https://github.com/everysoftware/fastapi-obs)

## OIDC configuration

You can get the OIDC configuration by visiting the `/.well-known/openid-configuration` endpoint.
Response example:

```json
{
  "issuer": "http://localhost:8000",
  "authorization_endpoint": "http://localhost:8000/authorize",
  "token_endpoint": "http://localhost:8000/api/v1/token",
  "userinfo_endpoint": "http://localhost:8000/api/v1/userinfo",
  "jwks_uri": "http://localhost:8000/.well-known/jwks.json",
  "scopes_supported": [
    "openid",
    "email",
    "name",
    "offline_access"
  ],
  "response_types_supported": [
    "code"
  ],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token"
  ],
  "subject_types_supported": [
    "public"
  ],
  "id_token_signing_alg_values_supported": [
    "RS256"
  ],
  "claims_supported": [
    "iss",
    "sub",
    "aud",
    "typ",
    "iat",
    "exp",
    "name",
    "given_name",
    "family_name",
    "email",
    "email_verified"
  ]
}
```

## Screenshots

![Sign In](assets/signin.png)
![Sign Up](assets/signup.png)
![Profile](assets/profile.png)
![Connections](assets/connections.png)
![Admin Login](assets/admin_login.png)
![Admin Apps](assets/admin_apps.png)
![Admin Users](assets/admin_users.png)

**Made with ❤️**
