import asyncio
import logging

import discord.utils

from setting import TOKEN
from src.extended_bot import ExtendedBot

extended_bot = ExtendedBot()

if __name__ == "__main__":
    discord.utils.setup_logging(level=logging.WARNING, root=False)
    asyncio.run(extended_bot.start(TOKEN))
