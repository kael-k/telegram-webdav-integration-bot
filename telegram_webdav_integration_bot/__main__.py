import logging

from telegram_webdav_integration_bot.bot import run_telegram_bot
from telegram_webdav_integration_bot.log import config_logging

log = logging.getLogger(__name__)


def main():
    config_logging()
    log.info("Starting telegram_webdav_integration_bot...")
    run_telegram_bot()


if __name__ == "__main__":
    main()
