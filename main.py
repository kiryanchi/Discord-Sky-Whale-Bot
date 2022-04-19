import os
import sys
import json
from discord import Intents

from src.whale import Whale


def main(env: str):
    with open("conf.json") as conf:
        config = json.load(conf)
    TOKEN = config["token"]
    intents = Intents.all()

    bot = Whale(command_prefix=".", intents=intents, env=env)

    bot.run(TOKEN)


if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    main(env)
