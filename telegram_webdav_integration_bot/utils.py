from datetime import datetime

DATE_FORMAT = "%Y%m%d_%H%M%S%f"


def get_now_str() -> str:
    return datetime.now().strftime(DATE_FORMAT)
