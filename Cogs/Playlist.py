import asyncio
from discord.ext import commands

from src.playlist.embed import Embed
from src.playlist.youtube import Youtube
from src.playlist.player import Player


class Playlist(commands.Cog, name="음악"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.players = {}

    @commands.Cog.listener()
    async def on_ready(self):
        servers = self.db.select_all_music_channel()
        if servers:
            for _, channel_id in servers:
                channel = self.bot.get_channel(channel_id)
                await self._create_playlist(channel)
        print("[INFO] 음악봇 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.channel not in self.bot.music_channel_list:
            return

        if message.content == f"{self.bot.command_prefix}초기화":
            await self.bot.process_command(message)
            return

        if message.content.startswith(self.bot.command_prefix):
            return

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            await asyncio.sleep(3)
            await message.delete()
            return

        if "list=" in message.content:
            return await message.channel.send("재생목록은 넣을 수 없습니다.", delete_after=3)

        if not self._check_youtube_link(message.content):
            link = await self._select_youtube_link(message)
        else:
            link = message.content

        if link:
            await self.players[message.guild].play(
                message=message, song=Youtube.extract_info(link=link)
            )

        await message.delete()

    @commands.command(
        name="초기화", help="이 채널을 음악봇이 사용합니다.", aliases=["init", "start", "시작"]
    )
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                if self.db.select_music_channel(ctx.guild.id):
                    self.db.delete_music_channel(ctx.guild.id)
                self.db.insert_music_channel(ctx.guild.id, ctx.channel.id)
            await self._create_playlist(ctx.channel)

        embed, components = Embed.start()
        components = [
            self.bot.components_manager.add_callback(component, callback)
            for component in components
        ]

        await ctx.send(embed=embed, components=components, delete_after=5)

    def _check_youtube_link(self, link):
        if "youtube.com" in link or "youtu.be" in link:
            return True

    async def _create_playlist(self, channel):
        await channel.purge()

        if channel in self.bot.music_channel_list:
            self.bot.music_channel_list.remove(channel)
        self.bot.music_channel_list.append(channel)

        playlist_msg = await channel.send(Embed.INIT_MSG)
        player = Player(
            bot=self.bot, playlist_channel=channel, playlist_msg=playlist_msg
        )
        await player.init()

        self.players[channel.guild] = player

        print(f"[INFO] [{channel.guild.name}] 길드 [{channel.name}] 채널 음악 봇 초기화 완료")

    async def _select_youtube_link(self, message):
        search = await Youtube.search(message=message)
        embed, components = Embed.search(message=message, search=search)

        # 유튜브 검색 후 9개 뽑아옴

        select_message = await message.channel.send(embed=embed, components=components)

        try:
            res = await self.bot.wait_for(
                "button_click",
                check=(
                    lambda interaction: message.author == interaction.user
                    and str(message.id) in interaction.custom_id
                ),
                timeout=15,
            )
            select = res.component.label
            if select == "Cancel":
                raise asyncio.exceptions.TimeoutError
            else:
                select = int(select)

        except asyncio.exceptions.TimeoutError:
            await select_message.delete()
            await message.channel.send("노래 선택이 취소되었습니다.", delete_after=5)
            return ""

        await select_message.delete()

        link = f"https://youtu.be/{search[select - 1]['id']}"

        return link


def setup(bot):
    bot.add_cog(Playlist(bot))
