from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext import commands

from src.components.music import Music
from src.components.search import Search
from src.components.song import Song
from src.db.music_channel import MusicChannel
from src.util.function import get_info
from src.util.log import logger

if TYPE_CHECKING:
    from discord import Message, Interaction, Member, VoiceState, User, TextChannel

    from src.extended_bot import ExtendedBot


class MusicCog(commands.GroupCog, name="고래"):
    def __init__(self, bot: ExtendedBot):
        self.bot = bot
        self.search = Search(bot)
        logger.debug("MusicCog 초기화 완료")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot or before.channel is None:
            return

        if music := self.bot.musics.get(before.channel.guild.id, None):
            if (
                self.bot.user in before.channel.members
                and len([user for user in before.channel.members if not user.bot]) == 0
            ):
                await music.reset()
                logger.info(f"{get_info(before.channel.guild)} 다 나가서 음악 봇 초기화")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        if music := self.bot.musics.get(message.guild.id, None):
            if message.channel != music.channel:
                return

            if message.author.voice is None:
                await message.reply("음성 채널에 들어가서 사용해주세요.", delete_after=5)
                await message.delete()
                return

            await self._play(
                music=music,
                link=message.content,
                user=message.author,
                channel=message.channel,
            )

            await message.delete()

    @app_commands.command(name="재생", description="재생목록에 노래을 추가합니다.")
    @app_commands.rename(value="노래")
    @app_commands.describe(value="링크 혹은 제목 입력")
    async def play(self, interaction: Interaction, value: str) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            if interaction.user.voice is None:
                await interaction.response.send_message(
                    "음성 채널에 들어가서 사용해주세요.", delete_after=5
                )
                return

            await interaction.response.defer(thinking=True)

            await self._play(
                music=music,
                link=value,
                user=interaction.user,
                channel=interaction.channel,
            )

            await interaction.delete_original_response()
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    @app_commands.command(name="시작", description="[관리자] 노래 채널을 생성합니다.")
    async def start(self, interaction: Interaction) -> None:
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("서버 관리 권한이 필요해요.", delete_after=5)
            return

        if self.bot.musics.get(interaction.guild_id, None):
            logger.debug(f"{get_info(interaction.guild)} 이미 음악 봇 존재")
            MusicChannel.delete(guild_id=interaction.guild_id)

        await interaction.response.defer(thinking=True)
        channel = await interaction.guild.create_text_channel(name="하늘-고래")
        self.bot.musics[channel.guild.id] = await Music.new(self.bot, channel)
        MusicChannel.add(MusicChannel(guild_id=channel.guild.id, channel_id=channel.id))
        logger.info(f"{get_info(interaction.guild)} 음악 채널 생성")
        await interaction.delete_original_response()

    @app_commands.command(name="초기화", description="노래봇이 이상할 때, 초기화합니다.")
    async def reset(self, interaction: Interaction) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            await music.reset(interaction)
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    @app_commands.command(name="일시정지", description="노래을 일시정지합니다.")
    async def pause(self, interaction: Interaction) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            await music.pause(interaction)
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    @app_commands.command(name="스킵", description="노래을 스킵합니다.")
    async def skip(self, interaction: Interaction) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            await music.skip(interaction)
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    @app_commands.command(name="셔플", description="재생목록을 한 번 흔듭니다.")
    async def shuffle(self, interaction: Interaction) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            await music.shuffle(interaction)
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    @app_commands.command(name="도움말", description="고래의 사용법을 알려줍니다.")
    async def help(self, interaction: Interaction) -> None:
        if music := self.bot.musics.get(interaction.guild_id, None):
            await music.help(interaction)
        else:
            await interaction.response.send_message(
                "하늘 고래가 없어요. 관리자에게 `/고래 시작` 명령어를 부탁하세요."
            )

    async def _play(self, music: Music, link: str, user: User, channel: TextChannel):
        if not self.is_youtube_link(link):
            logger.info(f"{get_info(channel.guild)} 노래 [{link}] 검색")
            searches = await self.search.from_youtube(link)

            if link.startswith("!"):
                link = searches[0].get("link")
            else:
                embed, view = self.search.make_ui(link, user, searches)
                select_message = await channel.send(
                    embed=embed, view=view, delete_after=15, silent=True
                )

                if not await view.wait():
                    link = view.link
                    asyncio.create_task(select_message.delete())

        if self.is_youtube_link(link):
            song = await Song.download(link, user)
            self.bot.loop.create_task(music.play(song, user))

    @staticmethod
    def is_youtube_link(link: str):
        return (
            link.startswith("http")
            and ("youtube.com" in link or "youtu.be" in link)
            and "playlist=" not in link
        )


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(MusicCog(bot))
