from setting import DEBUG, TOKEN
from src.tools import logger
from src.extended_bot import ExtendedBot


if __name__ == "__main__":
    if DEBUG:
        logger.debug("DEBUG 모드 설정")
    whale = ExtendedBot()
    whale.run(TOKEN)
