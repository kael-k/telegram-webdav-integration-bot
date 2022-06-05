import logging
import mimetypes
from typing import Union
from urllib.parse import urljoin
from uuid import uuid4

import requests
from telegram import Document, PhotoSize, Update, Video
from telegram.ext import CallbackContext, Dispatcher, Filters, MessageHandler, Updater

from telegram_webdav_integration_bot.env import EnvironmentConfig
from telegram_webdav_integration_bot.utils import get_now_str

log = logging.getLogger(__name__)
env_config = EnvironmentConfig()

UploadAttachment = Union[Document, Video, PhotoSize]


def get_logger(update: Update) -> logging.LoggerAdapter:
    if not update.effective_chat:
        log.warning(f"No chat_id found in update {update.update_id}")
        handler_log = logging.LoggerAdapter(log)
    else:
        handler_log = logging.LoggerAdapter(log, {"chat_id": update.effective_chat.id})
        handler_log.debug("Incoming message...")

    return handler_log


def error_handler(update: Update, context: CallbackContext):
    """
    Manage exception with a chat message
    """
    handler_log = get_logger(update)
    err = context.error
    handler_log.error(msg="Exception while handling an update:", exc_info=err)

    if hasattr(err, "message"):
        err_fqn = f"{err.__class__.__module__}.{err.__class__.__qualname__}"
        err_msg = f"{err_fqn}: {err.message}"
    else:
        err_msg = repr(err)

    update.effective_message.reply_text(
        "The bot encountered an error uploading the following file.\n"
        f"Exception {err_msg}"
    )


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
    handler_log = get_logger(update)

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
        res.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        handler_log.exception(f"Error during the upload of {filename} to WebDAV")
        raise e

    handler_log.info(f"Upload of {filename} successfully completed")


def run_telegram_bot():
    updater = Updater(env_config.TELEGRAM_BOT_TOKEN)
    dispatcher: Dispatcher = updater.dispatcher

    filters = Filters.photo | Filters.video | Filters.document | Filters.attachment
    if env_config.TELEGRAM_BOT_CHAT_IDS_DELIMITER:
        filters &= Filters.chat(env_config.TELEGRAM_BOT_CHAT_IDS)

    dispatcher.add_handler(MessageHandler(filters=filters, callback=process_message))
    dispatcher.add_error_handler(callback=error_handler)
    updater.start_polling()
    updater.idle()
