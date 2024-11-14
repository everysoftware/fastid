# FastID

Customizable and ready-to-use authorization server written in Python

## Key features

* Complies with OpenID Connect ✅
* Login via social networks. Support for Google, Telegram and Yandex at the moment 🔗
* One-time codes. Support for e-mail & telegram at the moment 🔢
* Admin panel to manage users & connected apps 👥
* Plugin system to extend the functionality ➕
* Metrics & tracing complied with OpenTelemetry 📊
* Written in Python using FastAPI ⚡

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

See [observability preset](https://github.com/everysoftware/fastapi-obs)

## Screenshots

![Admin Panel](assets/admin_panel.png)
![Metrics](assets/dashboard_metrics.png)
![Logs](assets/dashboards_logs.png)

**Made with ❤️**
