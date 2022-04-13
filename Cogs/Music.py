import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle

from Modules.Music.utils.embeds import Embed
from Modules.Music.components.playlist import Playlist


class Music(commands.Cog):
    def __init__(self, app):
        DiscordComponents(app)
        super().__init__()
        self.app = app

    @commands.command()
    async def vi(self, ctx):
        await ctx.send("vi")

    @commands.command("초기화")
    @commands.has_permissions(administrator=True)
    async def init(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                await ctx.send("하늘고래가 이곳을 향유하기 시작했어요.")
                await asyncio.sleep(2)
                await ctx.channel.purge()

                song = "> " + "{0:\u2000>30}".format("하늘고래")
                queue = "> " + "{0:\u2000>30}".format("sky whale")

                playlist = await ctx.send(
                    embed=Embed.playlist(song, queue),
                    components=[
                        [
                            Button(style=ButtonStyle.red, label="||"),
                            Button(style=ButtonStyle.green, label="▷"),
                            Button(style=ButtonStyle.blue, label="↻"),
                            Button(style=ButtonStyle.grey, label="?"),
                        ],
                        [
                            Button(style=ButtonStyle.grey, label="<"),
                            Button(style=ButtonStyle.grey, label=">"),
                            Button(style=ButtonStyle.grey, label="<<"),
                            Button(style=ButtonStyle.grey, label=">>"),
                        ],
                    ],
                )

                playlist = Playlist(playlist)

        embed = Embed.init()

        await ctx.send(
            embed=embed,
            components=[
                self.app.components_manager.add_callback(
                    Button(style=ButtonStyle.green, label="여기에 앉으렴"), callback
                ),
            ],
            delete_after=5,
        )
        await ctx.message.delete(delay=5)


def setup(app):
    app.add_cog(Music(app))
