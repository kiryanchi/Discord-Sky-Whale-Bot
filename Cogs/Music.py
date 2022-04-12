import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from db import DB

from youtubesearchpython import VideosSearch
import youtube_dl


class Youtube:
    def __init__(self):
        self.YDL_OPTS = {"foramt": "bestaudio", "quiet": True}
        self.NUM_OF_SEARCH = 9

    def search_music(self, amount):
        pass


class Music(commands.Cog):
    def __init__(self, app):
        DiscordComponents(app)
        super().__init__()
        self.app = app
        self.db = DB()

    def _make_player_embed(self, song_info=None):
        if song_info:
            embed = discord.Embed(
                title="현재 재생 중인 곡", description=song_info["title"], color=0xB18CFE
            )
            embed.set_image(url=song_info["thumbnail"])
            embed.set_footer(text="채팅을 치면 자동으로 검색합니다.")
        else:
            embed = discord.Embed(title="현재 재생 중 아님", color=0xB18CFE)
            embed.set_image(url="")
            embed.set_footer(text="채팅을 치면 자동으로 검색합니다.")
        return embed

    @commands.Cog.listener()
    async def on_message(self, message):
        # If bot, return
        if message.author == self.app.user:
            return

        # 음악 채널이면, 명령어로 취급하지 않음
        music_channel_data = self.db.select_music_channel(message.guild.id)
        if music_channel_data and music_channel_data[0][1] == message.channel.id:
            if message.content == ".초기화":
                await self.app.process_commands(message)
                return
            if message.content.startswith("."):
                pass

            # 음악 검색 시작
            if "youtube.com" in message.content:
                # TODO: Youtube 링크로 검색
                pass
            else:
                # TODO: 제목으로 검색
                pass
            await message.channel.send("음악 채널이네요")

    @commands.command("초기화")
    @commands.has_permissions(administrator=True)
    async def init(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                await self.handle_init(ctx)

        await ctx.send(
            "이 채널에서 음악봇을 시작할까요?\n`5초` 뒤 자동으로 취소됩니다.",
            components=[
                self.app.components_manager.add_callback(
                    Button(style=ButtonStyle.green, label="초기화"), callback
                ),
            ],
            delete_after=5,
        )
        await ctx.message.delete(delay=5)

    async def handle_init(self, ctx):
        # 길드내에 다른 음악 채널이 있다면, 삭제 후 DB 갱신
        if self.db.select_music_channel(ctx.guild.id):
            self.db.delete_music_channel(ctx.guild.id)

        # 음악봇 시작
        await ctx.send("이 채널에 음악봇을 시작합니다.")
        await asyncio.sleep(2)
        await ctx.channel.purge()

        # 기본적인 골격 맞추기
        await ctx.send("___***재생목록:***___")
        playlist = await ctx.send("재생목록")
        button = await ctx.send("버튼")

        player_embed = self._make_player_embed()
        await playlist.edit(
            "현재 재생목록이 비어있음",
            embed=player_embed,
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

        self.db.insert_music_channel(
            ctx.guild.id, ctx.channel.id, playlist.id, button.id
        )


def setup(app):
    app.add_cog(Music(app))
