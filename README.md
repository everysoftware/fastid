# FastID

**Effortless authentication solution for your services**

---

[![Test](https://github.com/everysoftware/fastid/actions/workflows/test.yml/badge.svg)](https://github.com/everysoftware/fastid/actions/workflows/test.yml)
[![CodeQL Advanced](https://github.com/everysoftware/fastid/actions/workflows/codeql.yml/badge.svg)](https://github.com/everysoftware/fastid/actions/workflows/codeql.yml)

---

## Features

FastID is responsible for authentication, user management and single account for all your applications.

The key features are:

* **Security**. Built with security in mind. It uses JWT tokens, OAuth 2.0 and OpenID Connect.
* **Admin Interface**. Comes with an admin interface to manage users and applications.
* **Social Login**. Supports social login with Google, Telegram, Yandex, and others.
* **Notifications**. Sends welcome messages and verification codes via email and Telegram.
* **Plugins**. Offers a plugin system to extend the functionality.
* **Observability**. Metrics and tracing complied with OpenTelemetry.
* **Pythonic**. FastID is the best choice for Python apps.

## Installation

1. Clone the repository:

     ```bash
     git clone https://github.com/everysoftware/fastid
     ```

2. Generate RSA keys:

     ```bash
     mkdir certs
     openssl genrsa -out certs/jwt-private.pem 2048
     openssl rsa -in certs/jwt-private.pem -pubout -out certs/jwt-public.pem
     ```

3. Create a `.env` file. Use the `.env.example` as a reference.

4. Run the application:

    ```bash
    make up
    ```

5. Enjoy!

FastID is now available at [http://localhost:8012](http://localhost:8012)

![Sign In](assets/signin.png)

API docs are available at [http://localhost:8012/api/v1/docs](http://localhost:8012/api/v1/docs)

![API Docs](assets/api_docs.png)

Admin is available at: [http://localhost:8012/admin](http://localhost:8012/admin) (default credentials:
`admin`/`admin`)

![Admin Login](assets/admin_login.png)

## Integration

1. Create new app in admin.

![Sign In](assets/create_app.png)

## OpenID Connect

Configuration is available
at [http://localhost:8012/.well-known/openid-configuration](http://localhost:8012/.well-known/openid-configuration).

The response will look like this:

```json
{
  "issuer": "http://localhost:8012",
  "authorization_endpoint": "http://localhost:8012/authorize",
  "token_endpoint": "http://localhost:8012/api/v1/token",
  "userinfo_endpoint": "http://localhost:8012/api/v1/userinfo",
  "jwks_uri": "http://localhost:8012/.well-known/jwks.json",
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
![Action Confirmation](assets/action_confirmation.png)
![Change Password](assets/change_password.png)
![Delete Account](assets/delete_account.png)
![Admin Login](assets/admin_login.png)
![Admin Apps](assets/admin_apps.png)
![Admin Users](assets/admin_users.png)

## Observability

**FastID** integrates perfectly with [this preset](https://github.com/everysoftware/fastapi-obs)

**Made with ❤️**
