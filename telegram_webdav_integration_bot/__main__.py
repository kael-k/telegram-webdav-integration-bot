import logging

log = logging.getLogger(__name__)


def main():
    log.info("Starting telegram-webdav-integration-bot...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
