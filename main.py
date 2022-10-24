from src.tools import Env, set_logger
from src.whale import Whale

DEFAULT_PREFIX = "."

logger = set_logger()

if __name__ == "__main__":
    env = Env()

    if env.environment == None or env.token == None:
        logger.error("환경 변수 확인 불가")
        exit()

    whale = Whale(prefix=DEFAULT_PREFIX, env=env)
    whale.run(env.token)
