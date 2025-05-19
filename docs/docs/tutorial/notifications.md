# Notifications

FastID supports sending notifications to users via **E-mail** and **Telegram**. This is useful for sending welcome message, OTPs,
and other important information.

## E-mail

You can use any SMTP server to send emails. The following example uses Gmail's SMTP server.

Add the following lines to your `.env` file:

```
NOTIFY_FROM_NAME="FastID"
NOTIFY_SMTP_HOST="smtp.gmail.com"
NOTIFY_SMTP_PORT=465
NOTIFY_SMTP_USERNAME=...
NOTIFY_SMTP_PASSWORD=...
```

## Telegram

Visit https://t.me/BotFather to create a new bot and obtain the token.

Add the following to your `.env` file:

```
TELEGRAM_ENABLED=1
TELEGRAM_BOT_TOKEN=...
```
