<p align="center">
    <a href="https://github.com/everysoftware/fastid"><img src="/assets/logo_text.png" alt="FastID"></a>
</p>
<p align="center">
    <em>FastID authentication platform, high security, lightning fast, easy-to-use, customizable.</em>
</p>

<p align="center">
    <a href="https://github.com/everysoftware/fastid/actions/workflows/test.yml" target="_blank">
        <img src="https://github.com/everysoftware/fastid/actions/workflows/test.yml/badge.svg" alt="Test">
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/everysoftware/fastid" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/everysoftware/fastid.svg" alt="Coverage">
    </a>
    <a href="https://github.com/everysoftware/fastid/actions/workflows/codeql.yml" target="_blank">
        <img src="https://github.com/everysoftware/fastid/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
    </a>
    <a href="https://github.com/everysoftware/fastid/actions/workflows/test.yml" target="_blank">
        <img src="https://img.shields.io/github/actions/workflow/status/everysoftware/fastid/test.yml?label=Bandit+Scan" alt="Bandit">
    </a>
    <a href="https://img.shields.io/github/license/everysoftware/fastid.png" target="_blank">
        <img src="https://img.shields.io/github/license/everysoftware/fastid.png" alt="License">
    </a>
</p>

---

**Live Demo:** https://fastid.croce.ru

**Documentation:** https://everysoftware.github.io/fastid

**Source Code:** https://github.com/everysoftware/fastid

---

## Features

* **Secure**: Reliable authentication without exposing user credentials to the clients (thanks
  to [OAuth 2.0](https://oauth.net/) and [OpenID Connect](https://openid.net/)).
* **Fast**: Powered by [FastAPI](https://fastapi.tiangolo.com/) (one of the fastest Python web frameworks
  available)
  and [SQLAlchemy](https://www.sqlalchemy.org/).
* **Easy-to-use**: Comes with an admin dashboard to manage users and applications. Built-in user profile pages for
  account management.
* **Quickly start**: Supports sign up with Google, Yandex, etc. Advanced integration with Telegram.
* **In touch with users**: Greets users after registration and verifies their actions via OTP.
* **Customizable**: Changes the appearance with custom templates for pages and email messages. Functionality can be
  extended with plugins.
* **Observable**: Monitor the platform's performance with 3 pills of observability: logging, metrics and tracing
  complied. Fully compatible with [OpenTelemetry](https://opentelemetry.io/).

## Installation

Clone the repository:

```bash
git clone https://github.com/everysoftware/fastid
```

Generate RSA keys:

```bash
make certs
```

Create a `.env` file based on `.env.example` and run the server:

```bash
make up
```

FastID is available at [http://localhost:8012](http://localhost:8012):

![Sign In](assets/signin.png)

Admin panel is available at: [http://localhost:8012/admin](http://localhost:8012/admin) (default credentials:
`admin`/`admin`):

![Admin Login](assets/admin_login.png)

> To set up observability, you can use [this](https://github.com/everysoftware/fastapi-obs) preset.

Enjoy! 🚀

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

**Made with ❤️**
