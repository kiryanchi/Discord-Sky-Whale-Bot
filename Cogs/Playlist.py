import discord
import asyncio
from discord.ext import commands

from src.playlist.embed import Embed
from src.playlist.player import Player


class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.guilds = {}

    @commands.Cog.listener()
    async def on_ready(self):
        servers = self.db.select_all_music_channel()
        if servers:
            for guild_id, channel_id in servers:
                channel = self.bot.get_channel(channel_id)
                await self._create_playlist(channel)
        print("[INFO] 음악봇 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel in self.bot.music_channel_list:
            return

        if message.content == f"{self.bot.command_prefix}초기화":
            await self.bot.process_command(message)
            return

        if message.content.startswith(self.bot.command_prefix):
            pass

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            await asyncio.sleep(3)
            return await message.delete()

        if "youtube.com" in message.content:
            await message.channel.send("youtube 주소 검색 기능은 구현중입니다...", delete_after=3)
            return

        print(f"[INFO] {message.content} 검색")

    @commands.command(neme="초기화", help="이 채널을 음악봇이 사용합니다.")
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

    async def _create_playlist(self, channel):
        async def callback(interaction):
            actions = {
                "pause": self._pause,
                "resume": self._resume,
                "shuffle": self._shuffle,
                "skip": self._skip,
                "prev": self._prev,
                "next": self._next,
                "first": self._first,
                "last": self._last,
            }
            await actions[interaction.custom_id]()

        embed, components_list = Embed.playlist()

        components = [
            [
                self.bot.components_manager.add_callback(component, callback)
                for component in components
            ]
            for components in components_list
        ]

        self.guilds[channel.guild] = {channel: Player(channel)}
        self.bot.music_channel_list.append(channel)

        await channel.send(embed=embed, components=components)

    async def _first(self, interaction):
        pass

    async def _next(self, interaction):
        pass

    async def _last(self, interaction):
        pass

    async def _pause(self, interaction):
        pass

    async def _prev(self, interaction):
        pass

    async def _resume(self, interaction):
        pass

    async def _shuffle(self, interaction):
        pass

    async def _skip(self, interaction):
        pass


def setup(bot):
    bot.add_cog(Playlist(bot))
