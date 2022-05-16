# telegram-webdav-integration-bot
Telegram bot consumer to send photo, videos and documents to webdav directory

## Build
To build the bot
```
podman build . -t telegram-webdav-integration-bot
```

An already built image is available on dockerhub: https://hub.docker.com/r/kaelk/telegram-webdav-integration-bot

## Run
To start the bot
```
podman run \
    -e TELEGRAM_BOT_API_KEY="<my-sercet-token>"
    -e TELEGRAM_BOT_CHAT_IDS="<chatid1>;<chatid2>;[...];<chatidn>"
    -e WEBDAV_USERNAME "<webdav-username>"
    -e WEBDAV_PASSWORD "<webdav-password>"
    -e WEBDAV_PATH_URL "<my webdav address: ex https://webdav.local/myfolder>"
    -e ENABLE_DEBUG "(0|1)"
    telegram-webdav-integration-bot
```

You `WEBDAV_USERNAME`, `WEBDAV_PASSWORD`, `ENABLE_DEBUG` (default "0"),
`TELEGRAM_BOT_CHAT_IDS` (default: does not filter by chat id) are optionals
