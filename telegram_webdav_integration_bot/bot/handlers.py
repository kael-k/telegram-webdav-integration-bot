import logging
from urllib.parse import urljoin

import requests
from telegram import Document, Update, Video
from telegram.ext import CallbackContext

from telegram_webdav_integration_bot.bot.utils import UploadAttachment
from telegram_webdav_integration_bot.env import EnvironmentConfig

from .log import get_logger
from .utils import get_filename

env_config = EnvironmentConfig()
log = logging.getLogger(__name__)


def error_handler(update: Update, context: CallbackContext):
    """
    Manage exception with a chat message
    """
    handler_log = get_logger(update, log)
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


def update_handler(update: Update, _: CallbackContext):
    handler_log = get_logger(update, log)

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
