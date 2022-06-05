import mimetypes
from typing import Union
from uuid import uuid4

from telegram import Document, PhotoSize, Video

from telegram_webdav_integration_bot.env import EnvironmentConfig
from telegram_webdav_integration_bot.utils import get_now_str

UploadAttachment = Union[Document, Video, PhotoSize]
env_config = EnvironmentConfig()


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
