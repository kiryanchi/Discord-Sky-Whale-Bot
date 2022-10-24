from discord import app_commands, Interaction, Message
from discord.ext import commands

from setting import MUSIC_CHANNEL_NAME
from src.cogs.music.service import MusicService
from src.tools import set_logger
from src.whale import Whale

log = set_logger()


class Music(commands.GroupCog, name="노래"):
    def __init__(self, bot: Whale):
        self.bot = bot
        self.service = MusicService(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        initialized_guilds = [
            {guild: channel.id}
            for guild in self.bot.guilds
            for channel in guild.channels
            if channel.name == MUSIC_CHANNEL_NAME
        ]

        log.info(f"모든 음악 채널을 초기화합니다.")
        for initialized_guild in initialized_guilds:
            for guild, channel_id in initialized_guild.items():
                await self.service.init_music_channel(guild, channel_id)
        log.info(f"모든 음악 채널을 초기화 완료했습니다.")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or message.channel.name != MUSIC_CHANNEL_NAME:
            return

        # TODO: DB 구현하기
        # TODO: command prefix 사용할것인가?
        # if message.content.startswith(self.bot.command_prefix):
        #     return

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            return await message.delete(delay=3)

        if "list=" in message.content:
            await message.channel.send("재생목록은 넣을 수 없습니다.", delete_after=3)
            return await message.delete(delay=3)

        await self.service.add_song_to_player(message)

    @app_commands.command(
        name="초기화", description="[관리자] 이 채널을 음악채널로 사용합니다. / 음악봇이 고장났을 때, 새로 시작합니다."
    )
    async def start_music_channel(self, interaction: Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            import asyncio

            await interaction.response.send_message("서버 관리 권한이 필요해요.")
            await asyncio.sleep(5)
            await interaction.delete_original_response()

            return

        await self.service.start_music_channel(interaction)

    @app_commands.command(name="추가", description="노래를 추가합니다.")
    @app_commands.rename(title="제목")
    async def add_music_to_queue(self, interaction: Interaction, title: str):
        # await interaction.response.send_message(f"{title} add_music_to_queue")
        # log.info(
        #     f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: 노래를 추가했습니다."
        # )
        return

    # @app_commands.command(name="목록", description="현재 재생목록을 확인합니다.")


async def setup(bot: Whale) -> None:
    await bot.add_cog(Music(bot))
