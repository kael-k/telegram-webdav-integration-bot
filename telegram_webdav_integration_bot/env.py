from os import environ


class EnvironmentConfig:
    """
    Load application environments variables
    This class can be instantiated everywhere in the program to loads the environment parameters
    """

    TELEGRAM_BOT_CHAT_IDS_DELIMITER = ";"

    def __init__(self):
        self.TELEGRAM_BOT_API_KEY = environ.get("TELEGRAM_BOT_API_KEY")
        if not environ.get("TELEGRAM_BOT_API_KEY"):
            raise EnvironmentError("Missing required env TELEGRAM_BOT_API_KEY")

        # process messages only for these chat_ids, if None do not filter chat id
        self.TELEGRAM_BOT_CHAT_IDS = None
        if environ.get("TELEGRAM_BOT_CHAT_IDS"):
            self.TELEGRAM_BOT_CHAT_IDS = [
                int(i)
                for i in environ.get("TELEGRAM_BOT_CHAT_IDS").split(
                    self.TELEGRAM_BOT_CHAT_IDS_DELIMITER
                )
            ]

        self.WEBDAV_PATH_URL = environ.get("WEBDAV_PATH_URL")
        # final slash urllib.parse.urljoin
        if self.WEBDAV_PATH_URL[-1] != "/":
            self.WEBDAV_PATH_URL += "/"

        if not environ.get("TELEGRAM_BOT_API_KEY"):
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
