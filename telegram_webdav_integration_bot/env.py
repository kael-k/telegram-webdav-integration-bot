from os import environ


class EnvironmentConfig:
    """
    Load application environments variables
    This class can be instantiated everywhere in the program to loads the environment parameters
    """

    TELEGRAM_BOT_CHAT_IDS_DELIMITER = ";"
    TELEGRAM_VALID_NAMING_CONVENTION = (
        "file-unique-id",
        "random-uuid",
        "date",
        "date+type",
    )

    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
        if not environ.get("TELEGRAM_BOT_TOKEN"):
            raise EnvironmentError("Missing required env TELEGRAM_BOT_TOKEN")

        # process messages only for these chat_ids, if None do not filter chat id
        self.TELEGRAM_BOT_CHAT_IDS = None
        if environ.get("TELEGRAM_BOT_CHAT_IDS"):
            self.TELEGRAM_BOT_CHAT_IDS = [
                int(i)
                for i in environ.get("TELEGRAM_BOT_CHAT_IDS").split(
                    self.TELEGRAM_BOT_CHAT_IDS_DELIMITER
                )
            ]

        # name generation for attachments that have no filename (such as videos and photos)
        self.TELEGRAM_FILE_NAMING_CONVENTION = environ.get(
            "TELEGRAM_FILE_NAMING_CONVENTION", "date+type"
        )
        if (
            self.TELEGRAM_FILE_NAMING_CONVENTION
            not in self.TELEGRAM_VALID_NAMING_CONVENTION
        ):
            raise EnvironmentError(
                f"TELEGRAM_FILE_NAMING_CONVENTION must be one of {', '.join(self.TELEGRAM_VALID_NAMING_CONVENTION)}"
            )
        self.TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION = (
            environ.get("TELEGRAM_FILE_NAMING_INCLUDE_EXTENSION", "1") == "1"
        )

        self.WEBDAV_PATH_URL = environ.get("WEBDAV_PATH_URL")
        # final slash urllib.parse.urljoin
        if self.WEBDAV_PATH_URL[-1] != "/":
            self.WEBDAV_PATH_URL += "/"

        if not environ.get("TELEGRAM_BOT_TOKEN"):
            raise EnvironmentError("Missing required env WEBDAV_PATH_URL")

        self.WEBDAV_USERNAME = environ.get("WEBDAV_USERNAME")
        self.WEBDAV_PASSWORD = environ.get("WEBDAV_PASSWORD")

        self.ENABLE_DEBUG = environ.get("ENABLE_DEBUG", "").lower() in [
            "1",
            "true",
            "t",
            "on",
            "yes",
            "y",
        ]
