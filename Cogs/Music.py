import asyncio
from typing import Dict
from discord.ext import commands

from Cogs.MusicComponents.playlist_embed import PlaylistEmbed
from Cogs.MusicComponents.playlist import Playlist
from Cogs.MusicComponents.youtube import Youtube
from Cogs.MusicComponents.song import Song
from src.db import DB

INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"

db = DB()


class Music(commands.Cog):
    guilds_playlist = {}
    youtube = None

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.playlist_embed: PlaylistEmbed = PlaylistEmbed()
        self.guilds_playlist: Dict[int, Playlist] = {}
        self.youtube = Youtube(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        servers = db.select_all_music_channel()
        for guild_id, channel_id in servers:
            guild = self.bot.get_guild(guild_id)
            channel = self.bot.get_channel(channel_id)
            await self.__handle_init_channel(channel)
            print(
                f"[INFO] [{guild.name:^10s}] 길드 [{channel.name:^10s}] 채널 음악 봇 초기화 완료"
            )  # Log

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.bot.music_channel_list:
            return

        if message.content == ".초기화":
            await self.bot.process_commands(message)
            return

        if message.content.startswith("."):
            pass

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            await asyncio.sleep(3)
            return await message.delete()

        if "youtube.com" in message.content:
            await message.channel.send("youtube 주소 검색 기능은 구현중입니다...", delete_after=3)
            return

        if (info := await self.youtube.search_and_select(message)) is None:
            return

        song = Song(info)

        playlist = self.guilds_playlist[message.guild.id]
        await playlist.play(message, song)

    @classmethod
    async def search(cls, message):
        if "youtube.com" in message.content:
            await message.channel.send("youtube 주소 검색 기능은 구현중이니다...", delete_after=3)
            return

        if (info := await cls.youtube.search_and_select(message)) is None:
            return

        song = Song(info)
        playlist = cls.guilds_playlist[message.guild.id]
        await playlist.play(message, song)

    @commands.command("초기화")
    @commands.has_permissions(administrator=True)
    async def init(self, ctx) -> None:
        async def callback(interaction):
            if interaction.user == ctx.author:
                if db.select_music_channel(ctx.guild.id):
                    db.delete_music_channel(ctx.guild.id)
                db.insert_music_channel(ctx.guild.id, ctx.channel.id)
            await self.__handle_init_channel(ctx.channel)

        embed, components = self.playlist_embed.init()
        components = [
            self.bot.components_manager.add_callback(component, callback)
            for component in components
        ]
        await ctx.send(embed=embed, components=components, delete_after=5)

    async def __handle_init_channel(self, channel):
        async def callback(interaction):
            playlist = self.guilds_playlist[interaction.guild.id]
            custom_id = interaction.custom_id

            if custom_id == "pause":
                playlist.pause()
                await interaction.send(
                    f"{interaction.author.name} 님이 일시정지를 했습니다.",
                    delete_after=3,
                    ephemeral=False,
                )
            elif custom_id == "resume":
                playlist.resume()
                await interaction.send(
                    f"{interaction.author.name} 님이 일시정지를 풀었습니다.",
                    delete_after=3,
                    ephemeral=False,
                )
            elif custom_id == "shuffle":
                await playlist.shuffle()
                await interaction.send(
                    f"{interaction.author.name}", delete_after=3, ephemeral=False
                )
            elif custom_id == "help":
                playlist.help()
                return
            elif custom_id == "skip":
                await playlist.skip()
                return
            elif custom_id == "prev_page":
                await playlist.prev_page()
            elif custom_id == "next_page":
                await playlist.next_page()
            elif custom_id == "first_page":
                await playlist.first_page()
            elif custom_id == "last_page":
                await playlist.last_page()
            elif custom_id == "Youtube":
                await playlist.youtube()

        await channel.purge()
        playlist = Playlist(text_channel=channel)

        embed, components_list = self.playlist_embed.playlist(playlist)
        components = [
            [
                self.bot.components_manager.add_callback(component, callback)
                for component in components
            ]
            for components in components_list
        ]
        playlist_msg = await channel.send(embed=embed, components=components)

        playlist.set_playlist_msg(playlist_msg)

        self.guilds_playlist[channel.guild.id] = playlist
        self.bot.add_music_channel(channel.id)


def setup(bot):
    bot.add_cog(Music(bot))
