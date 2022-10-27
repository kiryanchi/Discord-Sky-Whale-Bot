import logging
import logging.handlers
import os.path
import sys
from logging.handlers import TimedRotatingFileHandler

from rich.logging import RichHandler

LOG_PATH = "./log/botLog.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

if not os.path.exists("./log/"):
    os.makedirs("./log/")


def set_logger() -> logging.Logger:
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger = logging.getLogger("rich")

        logger.error(
            "Unexpected exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    logging.basicConfig(
        level="DEBUG",
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger("rich")
    sys.excepthook = handle_exception

    # file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler = TimedRotatingFileHandler(LOG_PATH, when="midnight", interval=1)
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger


logger = set_logger()
