import discord
from discord.ext import commands


class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.guilds = {}

    @commands.command(neme="초기화", help="이 채널을 음악봇이 사용합니다.")
    async def start(self):
        pass

    async def _create_playlist(self):
        pass


def setup(bot):
    bot.add_cog(Playlist(bot))
