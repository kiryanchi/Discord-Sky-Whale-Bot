import os

from dotenv import load_dotenv

from src.tools.log import set_logger

DEV_ENV = ".dev.env"
PROD_ENV = ".prod.env"

logger = set_logger()


class Env:
    def __init__(self) -> None:
        load_dotenv(verbose=True, dotenv_path=f".{os.getenv('ENV', '')}.env")
        logger.info(f"현재 개발 환경: {os.getenv('ENV')}, 환경 변수 로드 완료")

        self.environment = os.getenv("ENV", None)
        self.token = os.getenv("TOKEN", None)
