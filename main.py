import sys
import json
from discord import Intents

from src.whale import Whale


def main(env: str):
    with open("conf.json") as conf:
        config = json.load(conf)
    environment = config[env]
    intents = Intents.all()
    bot = Whale(command_prefix=".", intents=intents, environment=environment)

    bot.run(environment["token"])


if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    main(env)
