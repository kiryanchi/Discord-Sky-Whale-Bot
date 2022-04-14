import discord
from discord.ext import commands

from Modules.Music.components.queue import Queue


class Core(commands.Cog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.queue = Queue()

    @commands.command(name="클리어")
    async def clear(self, ctx):
        await ctx.channel.purge()

    @commands.command(name="핑")
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command(name="q")
    async def queue(self, ctx):
        await ctx.send(self.queue.queue)


def setup(app):
    app.add_cog(Core(app))
