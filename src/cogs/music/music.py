from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from discord import (
    Message,
    app_commands,
    Interaction,
    Guild,
    TextChannel,
    Member,
)
from discord.ext import commands
from discord.ext.commands import CommandInvokeError
from youtube_dl.utils import ExtractorError, DownloadError

from setting import DEFAULT_PREFIX
from src.cogs.music.components import Player, youtube_search, link_to_song
from src.cogs.music.view import YoutubeView, YoutubeEmbed
from src.model.music_channel import MusicChannel
from src.tools import logger

if TYPE_CHECKING:
    from src.whale import Whale

INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"


class Music(commands.GroupCog, name="노래"):
    def __init__(self, bot: Whale) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("모든 음악 채널 초기화")

        for music_channel in MusicChannel.get_all():
            guild = self.bot.get_guild(music_channel.guild_id)
            channel = self.bot.get_channel(music_channel.channel_id)
            await self.initialize(guild, channel)

        logger.info("모든 음악 채널 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if (not message.guild.id in self.bot.players) or (  # 음악봇이 초기화 되지 않았거나
            message.channel
            != self.bot.players[message.guild.id].channel  # 음악 채널이 아닌 경우
        ):
            return

        if message.content.startswith(DEFAULT_PREFIX):
            return

        await message.delete()

        await self.add_song_to_player(
            channel=message.channel, content=message.content, author=message.author
        )

    @app_commands.command(name="시작", description="[관리자] 이 채널을 음악채널로 사용합니다.")
    async def make_music_channel_command(self, interaction: Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("서버 관리 권한이 필요해요.")
            await asyncio.sleep(5)
            return await interaction.delete_original_response()

        await interaction.response.defer(thinking=True)

        if MusicChannel.get(interaction.guild_id):
            logger.info(
                f"{interaction.guild_id}|{interaction.guild} 길드에 이미 음악채널이 있습니다."
            )
            MusicChannel.delete(interaction.guild_id)

        MusicChannel.add(
            MusicChannel(
                guild_id=interaction.guild.id, channel_id=interaction.channel.id
            )
        )

        await self.initialize(interaction.guild, interaction.channel)

    @app_commands.command(name="초기화", description="음악봇이 이상할 때, 새로 초기화합니다.")
    async def reset_music_channel_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await self.initialize(interaction.guild, interaction.channel)

    @app_commands.command(name="재생", description="노래를 재생합니다.")
    @app_commands.rename(title="제목or링크")
    async def add_song_to_player_command(self, interaction: Interaction, title: str):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await interaction.response.defer(thinking=True)
        # await interaction.delete_original_response()
        await (await interaction.original_response()).delete()

        await self.add_song_to_player(
            channel=interaction.channel, content=title, author=interaction.user
        )
        return

    @app_commands.command(name="일시정지", description="음악 재생을 잠깐 중단합니다.")
    async def pause_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await self.bot.players[interaction.guild_id].pause(interaction)

    @app_commands.command(name="정지해제", description="일시정지를 해제합니다.")
    async def resume_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await self.bot.players[interaction.guild_id].resume(interaction)

    @app_commands.command(name="셔플", description="재생목록을 한 번 섞습니다.")
    async def shuffle_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await self.bot.players[interaction.guild_id].shuffle(interaction)

    @app_commands.command(name="스킵", description="노래를 스킵합니다.")
    async def skip_song_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        await self.bot.players[interaction.guild_id].skip(interaction)

    @app_commands.command(name="현재", description="현재 재생중인 노래 정보를 가져옵니다.")
    async def current_song_command(self, interaction: Interaction):
        if self.is_init_music_channel(interaction):
            return await interaction.response.send_message(
                "`시작` 명령어로 음악 채널을 먼저 설정해주세요."
            )
        song = self.bot.players[interaction.guild_id].current_song
        if song:
            await interaction.response.send_message(content=f"{song}", ephemeral=True)
            await self.bot.players[interaction.guild_id].youtube(interaction)

    async def is_init_music_channel(self, interaction: Interaction):
        return interaction.guild_id in self.bot.players

    async def initialize(self, guild: Guild, channel: TextChannel):
        if guild in self.bot.players:
            await self.bot.players[guild.id].leave()

        await channel.purge()

        playlist = await channel.send(INIT_MSG)
        player = Player(bot=self.bot, playlist=playlist)
        self.bot.players[guild.id] = player
        await player.update_playlist()  # TODO: update_playlist()

        logger.info(f"[{guild.id} | {guild}] 음악 채널 초기화")

    async def add_song_to_player(
        self, channel: TextChannel, content: str, author: Member
    ):
        if author.voice is None:
            return await channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)

        if "list=" in content:
            return await channel.send("재생목록은 넣을 수 없습니다.", delete_after=3)

        if "youtube.com" in content or "youtu.be" in content:
            link = content
        else:
            result = await youtube_search(content)

            view = YoutubeView()
            embed = YoutubeEmbed(content, result)
            search_result_message = await channel.send(
                embed=embed, view=view, delete_after=15
            )

            await view.wait()

            if view.value is None:
                return

            await search_result_message.delete()
            link = result[int(view.value) - 1]["link"]

        try:
            song = await link_to_song(link)
        except ExtractorError or DownloadError or CommandInvokeError:
            await channel.send(f"Youtube 링크가 올바르지 않아요.", delete_after=3)

        await self.bot.players[channel.guild.id].play(channel, song, author)


async def setup(bot: Whale) -> None:
    await bot.add_cog(Music(bot))
