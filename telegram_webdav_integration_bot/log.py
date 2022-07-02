import logging

from telegram_webdav_integration_bot.env import EnvironmentConfig


class LogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        default_attrs = logging.LogRecord(
            record.name,
            record.levelno,
            record.pathname,
            record.lineno,
            None,
            None,
            None,
        ).__dict__.keys()
        extras = set(record.__dict__.keys()) - default_attrs

        format_str = "[%(asctime)sZ][%(levelname)s][%(name)s]: %(message)s"
        if "chat_id" in extras:
            format_str = f"[%(asctime)sZ][%(levelname)s][%(name)s][chat_id={record.__dict__['chat_id']}]: %(message)s"

        self._style._fmt = format_str

        return super().format(record)


def config_logging():
    """
    Setup application logging
    """
    env_config = EnvironmentConfig()

    logger = logging.root
    handler = logging.StreamHandler()
    formatter = LogFormatter()
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG if env_config.ENABLE_DEBUG else logging.INFO)
    logger.addHandler(handler)
