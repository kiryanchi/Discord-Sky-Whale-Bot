import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle

from Modules.Music.utils.embeds import Embed
from Modules.Music.utils.components import Components
from Modules.Music.components.playlist import Playlist
from Modules.Music.components.youtube import Youtube


class Music(commands.Cog):
    def __init__(self, app):
        DiscordComponents(app)
        super().__init__()
        self.app = app

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 962232434613710878:
            return

        if message.author == self.app.user:
            return

        if message.content.startswith("."):
            await self.app.process_commands(message)
            return

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            return await message.delete()

        info = await self.app.loop.run_in_executor(
            None, lambda: Youtube.search(message.content)
        )
        song = await Youtube.select(self.app, message, info)

        print(song)

    @commands.command("초기화")
    @commands.has_permissions(administrator=True)
    async def init(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                await Music._init_channel(ctx.channel)

        embed = Embed.init()
        components = Components.init()[0]

        await ctx.send(
            embed=embed,
            components=[
                self.app.components_manager.add_callback(components, callback),
            ],
            delete_after=5,
        )
        await ctx.message.delete(delay=5)

    @staticmethod
    async def _init_channel(channel):
        await channel.send("하늘고래가 이곳을 향유하기 시작했어요.")
        await asyncio.sleep(2)
        await channel.purge()

        song = "> " + "{0:\u2000>30}".format("하늘고래")
        queue = "> " + "{0:\u2000>30}".format("sky whale")

        playlist = await channel.send(
            embed=Embed.playlist(song, queue), components=Components.playlist()
        )

        playlist = Playlist(playlist)


def setup(app):
    app.add_cog(Music(app))
