import random
import asyncio
import discord
from discord.ext import commands


from src.utils.queue import Queue


class Player:
    def __init__(self):
        self.voice_channel = None
        self.voice_client = None
        self.playing = False
        self.songs = {"current_song": None, "next_songs": []}

    def pause(self):
        if self.voice_client is None:
            return
        if not self.voice_client.is_paused():
            self.voice_client.pause()

    def resume(self):
        if self.voice_client is None:
            return
        if self.voice_client.is_paused():
            self.voice_client.resume()

    async def shuffle(self):
        if not self.songs["next_songs"]:
            return
        random.shuffle(self.songs["next_songs"])


class Playlist(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.__bot = bot
        self.__db = bot.db
        self.__guilds = {}

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = self.db.select_all_music_channel()
        channels = [channel_id for _, channel_id in guilds]
        map(lambda channel: self.__init_channel(self.bot, channel), channels)
        print(f"[INFO] {self.__class__.__name__} 초기화 완료")  # Log

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if (playlist := self.queue[message.guild.id]) is None:
            return


def setup(bot):
    bot.add_cog(Playlist(bot))
