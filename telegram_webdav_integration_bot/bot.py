import logging
import mimetypes
from typing import Union
from urllib.parse import urljoin
from uuid import uuid4

import requests
from telegram import Document, PhotoSize, Update, Video
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

from telegram_webdav_integration_bot.env import EnvironmentConfig
from telegram_webdav_integration_bot.utils import get_now_str

log = logging.getLogger(__name__)
env_config = EnvironmentConfig()

UploadAttachment = Union[Document, Video, PhotoSize]


def get_filename(attachment: UploadAttachment):
    if hasattr(attachment, "file_name") and attachment.file_name:
        return attachment.file_name

    extension = ""
    if env_config.TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION:
        if hasattr(attachment, "mime_type"):
            extension = mimetypes.guess_extension(attachment.mime_type or "") or ""
        else:
            if isinstance(attachment, PhotoSize):
                extension = ".jpg"

    if env_config.TELEGRAM_FILE_NAMING_CONVENTION == "file-unique-id":
        return f"{attachment.file_unique_id}{extension}"
    if env_config.TELEGRAM_FILE_NAMING_CONVENTION == "random-uuid":
        return f"{uuid4().hex}{extension}"
    if env_config.TELEGRAM_FILE_NAMING_CONVENTION == "date":
        return f"{get_now_str()}{extension}"
    if env_config.TELEGRAM_FILE_NAMING_CONVENTION == "date+type":
        filetype = "file"
        if isinstance(attachment, Video):
            filetype = "video"
        if isinstance(attachment, PhotoSize):
            filetype = "image"
        return f"{get_now_str()}-{filetype}{extension}"


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

    attachment: UploadAttachment
    filename: str

    if isinstance(message.effective_attachment, list):
        if not len(message.effective_attachment):
            handler_log.warning("Skipping attachment, empty list of PhotoSize")
            return
        attachment = sorted(
            message.effective_attachment,
            key=lambda x: int(x.file_size or 0),
            reverse=True,
        )[0]
    elif isinstance(message.effective_attachment, (Document, Video)):
        attachment = message.effective_attachment
    else:
        handler_log.warning(
            "Skipping attachment file, the bot do not know "
            + f"how to manage attachment type {type(message.effective_attachment)}"
        )
        return

    filename = get_filename(attachment)
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
        return

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
