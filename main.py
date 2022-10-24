from setting import DEBUG, TOKEN
from src.tools import logger
from src.whale import Whale


if __name__ == "__main__":
    if DEBUG:
        logger.debug("DEBUG 모드 설정")
    whale = Whale()
    whale.run(TOKEN)
