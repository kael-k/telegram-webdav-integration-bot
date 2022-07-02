import logging
from logging import Logger

from telegram import Update


def get_logger(update: Update, log: Logger) -> logging.LoggerAdapter:
    if not update.effective_chat:
        log.warning(f"No chat_id found in update {update.update_id}")
        handler_log = logging.LoggerAdapter(log)
    else:
        handler_log = logging.LoggerAdapter(log, {"chat_id": update.effective_chat.id})
        handler_log.debug("Incoming message...")

    return handler_log
