import logging


levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class MyLogger:
    def __init__(self, level):
        self.__logger = logging.getLogger("myLogger")
        self.__logger.setLevel(levels[level])

        stream_handler = logging.StreamHandler()
        self.__logger.addHandler(stream_handler)

    def debug(self, log):
        print(f"[DEBUG] {log}")

    def info(self, log):
        print(f"[INFO] {log}")

    def warning(self, log):
        print(f"[WARNING] {log}")
