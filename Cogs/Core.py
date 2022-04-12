import discord
from discord.ext import commands


class Core(commands.Cog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app

    @commands.command(name="클리어")
    async def clear(self, ctx):
        await ctx.channel.purge()

    @commands.command(name="핑")
    async def ping(self, ctx):
        await ctx.send("pong")


def setup(app):
    app.add_cog(Core(app))
