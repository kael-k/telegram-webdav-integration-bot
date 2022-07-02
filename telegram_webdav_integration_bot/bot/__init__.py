import logging

from telegram.ext import Dispatcher, Filters, MessageHandler, Updater

from telegram_webdav_integration_bot.bot.handlers import error_handler, update_handler
from telegram_webdav_integration_bot.env import EnvironmentConfig

log = logging.getLogger(__name__)
env_config = EnvironmentConfig()


def run_telegram_bot():
    updater = Updater(env_config.TELEGRAM_BOT_TOKEN)
    dispatcher: Dispatcher = updater.dispatcher

    filters = Filters.photo | Filters.video | Filters.document | Filters.attachment
    if env_config.TELEGRAM_BOT_CHAT_IDS_DELIMITER:
        filters &= Filters.chat(env_config.TELEGRAM_BOT_CHAT_IDS)

    dispatcher.add_handler(MessageHandler(filters=filters, callback=update_handler))
    dispatcher.add_error_handler(callback=error_handler)
    updater.start_polling()
    updater.idle()


__all__ = ["run_telegram_bot"]
