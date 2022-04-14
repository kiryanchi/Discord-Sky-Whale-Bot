import asyncio
from discord.ext import commands
from discord_components import DiscordComponents

from Modules.Music.utils.embeds import Embed
from Modules.Music.utils.components import Components
from Modules.Music.components.playlist import Playlist
from Modules.Music.components.youtube import Youtube
from Modules.Music.components.queue import Queue
from Modules.Music.components.song import Song
from db import DB


playlist_queue = Queue()
msg = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [35m향유[0m하기 시작했어요\n```"


class Music(commands.Cog):
    def __init__(self, app):
        DiscordComponents(app)
        super().__init__()
        self.app = app
        self.db = DB()

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = self.db.select_all_music_channel()

        for guild in guilds:
            _, channel_id = guild

            channel = self.app.get_channel(channel_id)
            await Music._init_channel(self.app, channel)

        print("Music bot init done")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.app.user:
            return

        if (
            playlist_queue[message.guild.id]
            and message.channel.id == playlist_queue[message.guild.id].get_channel_id()
        ):
            if message.content == ".초기화":
                await self.app.process_commands(message)
                return

            if message.content.startswith("."):
                pass

            if message.author.voice is None:
                await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
                await asyncio.sleep(3)
                return await message.delete()

            if "youtube.com" in message.content:
                # Yotube play
                await message.channel.send("youtube 주소 검색 기능은 구현중입니다..", delete_after=3)
                return

            if (info := await Youtube.search_and_select(self.app, message)) is None:
                return

            song = Song(info)

            playlist: Playlist = playlist_queue[message.guild.id]
            await playlist.play(message, song)

    @commands.command("초기화")
    @commands.has_permissions(administrator=True)
    async def init(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                if self.db.select_music_channel(ctx.guild.id):
                    self.db.delete_music_channel(ctx.guild.id)
                self.db.insert_music_channel(ctx.guild.id, ctx.channel.id)
                await Music._init_channel(self.app, ctx.channel)

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

    @classmethod
    async def _init_channel(cls, app, channel):
        await channel.purge()
        playlist_msg = await channel.send(msg)

        playlist = Playlist(app=app, channel=channel, playlist_msg=playlist_msg)

        await playlist_msg.edit(
            embed=Embed.playlist(playlist), components=Components.playlist()
        )

        playlist_queue[channel.guild.id] = playlist


def setup(app):
    app.add_cog(Music(app))
