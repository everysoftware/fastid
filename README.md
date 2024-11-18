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

## Screenshots

![Sign In](assets/signin.png)
![Sign Up](assets/signup.png)
![Profile](assets/profile.png)
![Connections](assets/connections.png)
![Admin Login](assets/admin_login.png)
![Admin Apps](assets/admin_apps.png)
![Admin Users](assets/admin_users.png)

**Made with ❤️**
