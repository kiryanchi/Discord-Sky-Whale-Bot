import os
import discord
from discord.ext import commands, tasks
from discord_components import ComponentsBot
from itertools import cycle

from src.db import DB

GAME_LIST = cycle(["재획", "유튜브 검색", "일", "모교는"])


class Whale(ComponentsBot):
    def __init__(self, command_prefix, intents, environment):
        super().__init__(
            command_prefix=environment["default_command_prefix"], intents=intents
        )
        self.music_channel_list = []
        self.db = DB(environment["db"])

        self.remove_command("help")

        for filename in os.listdir("Cogs"):
            if filename.endswith(".py"):
                print(f"[INFO] 명령어 [{filename[:-3]:^15s}] 로드 완료")  # Log
                self.load_extension(f"Cogs.{filename[:-3]}")

    def add_music_channel(self, channel_id):
        self.music_channel_list.append(channel_id)

    async def on_ready(self):
        print("[INFO] 하늘 고래 봇 시작")  # Log

        @tasks.loop(minutes=30)
        async def change_game():
            await self.change_presence(activity=discord.Game(next(GAME_LIST)))

        change_game.start()

        print("[INFO] 하늘 고래가 하늘을 납니다.")  # Log

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.channel.id in self.music_channel_list:
            if message.content.startswith(self.command_prefix):
                return

        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("권한이 없어요", mention_author=True)

        if isinstance(error, commands.CommandNotFound):
            await ctx.reply("그런 명령어는 없어요", mention_author=True)
