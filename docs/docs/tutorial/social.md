# Social Login

Social login allows users to authenticate using their existing accounts from popular platforms like **Google**, **Yandex**, and
**Telegram**. This can simplify the registration process and improve user experience.

## Google

Visit https://console.cloud.google.com/apis/credentials to obtain client credentials.

Add the following to your `.env` file:

```
GOOGLE_ENABLED=1
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## Yandex

Visit https://oauth.yandex.ru to obtain client credentials.

Add the following to your `.env` file:

```
YANDEX_ENABLED=1
YANDEX_CLIENT_ID=...
YANDEX_CLIENT_SECRET=...
```

## Telegram

Visit https://t.me/BotFather to create a new bot and obtain the token. Set the domain for the bot in the BotFather
settings.

Add the following to your `.env` file:

```
TELEGRAM_ENABLED=1
TELEGRAM_BOT_TOKEN=...
```
