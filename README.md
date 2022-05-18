# Telegram WebDAV Integration Bot
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue?style=flat-square&logo=python)](LICENSE)
[![GPLv3 License](https://img.shields.io/badge/license-GPLv3-green?style=flat-square&logo=legal)](LICENSE)
[![Code style: black](https://img.shields.io/badge/black-v22.3.0-orange?style=flat-square)](https://github.com/psf/black)
[![Code style: mypy](https://img.shields.io/badge/mypy-v0.950-orange?style=flat-square)](https://github.com/python/mypy)
[![Code style: flake8](https://img.shields.io/badge/flake8-3.9.0-orange?style=flat-square)](https://github.com/PyCQA/flake8)


A Telegram bot that scrape from chats images, videos and files and send them to a WebDAV server.

An already built container image is available on [Docker Hub](https://hub.docker.com/r/kaelk/telegram-webdav-integration-bot).

## Usage
First, you'll need to setup a bot on telegram https://core.telegram.org/bots#3-how-do-i-create-a-bot.

After you generated the token, you can run the software via podman/docker (or your preferred container runtime):
```
podman run \
    -e TELEGRAM_BOT_TOKEN="<my-sercet-token>" \
    -e WEBDAV_PATH_URL "<my webdav address: ex https://webdav.local/myfolder>" \
    -e TELEGRAM_BOT_CHAT_IDS="[<chatid1>[;<chatid2>;<...>;<chatidn>]]" \
    -e WEBDAV_USERNAME "<webdav-username>" \
    -e WEBDAV_PASSWORD "<webdav-password>" \
    -e TELEGRAM_FILE_NAMING_CONVENTION "date+type" \
    -e TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION "1" \
    -e ENABLE_DEBUG "(0|1)" \
    kaelk/telegram-webdav-integration-bot
```

* `ENABLE_DEBUG` by default is "0", i you do not need debug you can omit the env
* if your WebDAV service doesn't need authn, omit envs `WEBDAV_USERNAME` and `WEBDAV_PASSWORD`
* also `TELEGRAM_BOT_CHAT_IDS` is optional, however this means that **EVERYONE** can send a message to the bot
and they will **ALL** be processed
* `TELEGRAM_FILE_NAMING_CONVENTION` and `TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION` are for generating names
for attachments that doesn't have one:
  * `TELEGRAM_FILE_NAMING_CONVENTION`: which method use to generate file name, valid values:
    * `file-unique-id`: use telegram file unique id
    * `random-uuid`: use a random UUID4
    * `date`: use datetime
    * `date+type` (default): use datetime ad append the file type ("image", "video"...)
  * `TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION` (default '1') try to automatically guess a valid extension

## Build

### Container

To build the bot in container:
```
podman build . -t telegram-webdav-integration-bot
```

### Source
All dependencies are listed in `requirements.txt`.
If you want to contribute, you'll also need to install `pre-commit` to check the code quality.
