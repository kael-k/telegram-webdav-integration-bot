import logging
from typing import Sequence
from urllib.parse import urljoin

import requests
from telegram import Document, PhotoSize, Update, Video
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

from telegram_webdav_integration_bot.env import EnvironmentConfig

log = logging.getLogger(__name__)
env_config = EnvironmentConfig()


def process_message(update: Update, _: CallbackContext):
    if not update.effective_chat:
        log.warning(f"No chat_id found in update {update.update_id}")
        handler_log = logging.LoggerAdapter(log)
    else:
        handler_log = logging.LoggerAdapter(log, {"chat_id": update.effective_chat.id})
        handler_log.debug("Incoming message...")

    if not (message := update.effective_message):
        raise ValueError("No message found in chat...")

    if not message.effective_attachment:
        handler_log.debug("No attachmet in  Incoming message...")
        return

    attachments: Sequence[Document | Video | PhotoSize]
    if isinstance(message.effective_attachment, list):
        attachments = message.effective_attachment
    elif isinstance(message.effective_attachment, (Document, Video)):
        attachments = [message.effective_attachment]

    for attachment in attachments:
        if isinstance(attachment, (Document, Video)):
            filename = attachment.file_name
        elif isinstance(attachment, PhotoSize):
            filename = f"{attachment.file_unique_id}.jpg"
        else:
            handler_log.warning(
                f"Skipping attachment file with id: {attachment.file_id},"
                + f" the bot do not know how to manage attachment type {type(attachment)}"
            )
            continue

        raw_attachment = attachment.get_file().download_as_bytearray()
        url = urljoin(env_config.WEBDAV_PATH_URL, filename, allow_fragments=False)

        webdav_auth = None
        if env_config.WEBDAV_USERNAME and env_config.WEBDAV_PASSWORD:
            webdav_auth = (env_config.WEBDAV_USERNAME, env_config.WEBDAV_PASSWORD)

        handler_log.info(f"Uploading file {filename} to WebDAV...")
        try:
            res = requests.put(url, raw_attachment, auth=webdav_auth)
        except requests.exceptions.RequestException:
            handler_log.exception(f"Error during the upload of {filename} to WebDAV")
            continue

        if res.ok:
            handler_log.info(f"Upload of {filename} successfully completed")
        else:
            handler_log.error(
                f"Error during the upload of {filename} to WebDAV, server responded {res.status_code} {res.reason}"
            )


def run_telegram_bot():
    updater = Updater(env_config.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    filters = Filters.photo | Filters.video | Filters.document | Filters.attachment
    if env_config.TELEGRAM_BOT_CHAT_IDS_DELIMITER:
        filters &= Filters.chat(env_config.TELEGRAM_BOT_CHAT_IDS)

    dispatcher.add_handler(MessageHandler(filters=filters, callback=process_message))
    updater.start_polling()
    updater.idle()
