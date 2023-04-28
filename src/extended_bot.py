import glob
import platform
import random

from discord import Intents, opus, Activity
from discord.ext import tasks
from discord.ext.commands import Bot, when_mentioned

from setting import DEBUG, ADMIN_GUILD, ACTIVITIES
from src.components.music import Music
from src.db.music_channel import MusicChannel
from src.util.log import logger


class ExtendedBot(Bot):
    musics: dict[int, Music] = {}

    def __init__(self):
        super().__init__(intents=Intents.all(), command_prefix=when_mentioned)

    async def setup_hook(self) -> None:
        if not opus.is_loaded():
            self.load_opus()
        logger.info("opus 로드 완료")

        await self.load_cogs()
        logger.info("cogs 로드 완료")

        await self.sync_cogs()
        logger.info(f"{'길드' if DEBUG else '서버'} 명령어 등록 완료")

    async def on_ready(self) -> None:
        @tasks.loop(minutes=30)
        async def change_activity():
            _name, _type = random.choice(ACTIVITIES)
            await self.change_presence(activity=Activity(name=_name, type=_type))
            logger.debug(f"하늘고래 {_name} {_type}")

        await self.init_musics()
        logger.info("음악 채널 초기화 완료")

        change_activity.start()
        logger.info(f"{self.user} 로그인 성공")

    async def load_cogs(self):
        for cog in glob.glob("./src/cogs/*.py"):
            cog = cog[2:-3].replace("/", ".")
            await self.load_extension(cog)
            logger.debug(f"명령어 [{cog}] 로드")

    async def sync_cogs(self):
        if DEBUG:
            self.tree.copy_global_to(guild=ADMIN_GUILD)
        await self.tree.sync(guild=ADMIN_GUILD if DEBUG else None)

    async def init_musics(self):
        for music_channel in MusicChannel.get_all():
            guild = self.get_guild(music_channel.guild_id)
            channel = self.get_channel(music_channel.channel_id)
            if guild and channel:
                self.musics[music_channel.guild_id] = await Music.new(self, channel)
                continue
            MusicChannel.delete(music_channel.guild_id)
            logger.info(f"{music_channel} 삭제됨")

    @staticmethod
    def load_opus():
        if platform.system() == "Darwin":
            opus.load_opus(
                glob.glob("/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib")[0]
            )
            logger.debug("macOS 확인. opus를 다시 불러옵니다")
