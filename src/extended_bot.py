from __future__ import annotations

import glob
import platform
import random
from typing import Dict
from typing import TYPE_CHECKING

from discord import Intents, Object, Guild, opus, ActivityType, Activity
from discord.ext import commands, tasks

from setting import COMMANDS, DEBUG, DEFAULT_PREFIX, ADMIN_GUILD_ID
from src.model.music_channel import MusicChannel
from src.tools import logger

if TYPE_CHECKING:
    from src.cogs.music.components import Player

ACTIVITIES = [
    # 듣는 중
    ("노래", ActivityType.listening),
    # 하는 중
    ("향유", ActivityType.playing),
    ("게임", ActivityType.playing),
    ("유튜브 검색", ActivityType.playing),
    # 시청 중
    ("넷플릭스", ActivityType.watching),
    ("유튜브", ActivityType.watching),
]

ADMIN_GUILD = Object(id=ADMIN_GUILD_ID)


async def load_darwin_opus():
    if platform.system() == "Darwin":
        logger.debug("macOS 확인. opus 다시 불러옵니다.")
        opus.load_opus(glob.glob("/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib")[0])


class ExtendedBot(commands.Bot):
    players: Dict[int, Player] = {}

    def __init__(self):
        super().__init__(intents=Intents.all(), command_prefix=DEFAULT_PREFIX)

    async def setup_hook(self) -> None:

        await load_darwin_opus()
        logger.info("opus 로드")

        await self.load_cogs()
        logger.info(f"명령어 로드")

        await self.sync_command()
        logger.info(f"{'길드' if DEBUG else '서버'} 명령어 등록 완료")

    async def on_ready(self):
        @tasks.loop(minutes=30)
        async def change_activity():
            _name, _type = random.choice(ACTIVITIES)
            await self.change_presence(activity=Activity(name=_name, type=_type))
            logger.debug(f"상태 변경: {_name} {_type}")

        await self.delete_unchecked_guilds()
        logger.info("DB 정리 완료")

        change_activity.start()
        logger.info(f"{self.user} 로그인 성공")

    async def on_guild_remove(self, guild: Guild):
        if self.players.pop(guild.id, None) is None:
            return logger.info(f"[{guild.id} | {guild}] DB에 등록되지 않은 길드입니다.")
        MusicChannel.delete(guild.id)
        logger.info(f"[{guild.id} | {guild}] 음악 채널 삭제")

    async def sync_command(self):
        if DEBUG:
            self.tree.copy_global_to(guild=ADMIN_GUILD)
        await self.tree.sync(guild=ADMIN_GUILD if DEBUG else None)

    async def load_cogs(self):
        for command in COMMANDS:
            await self.load_extension(f"src.cogs.{command}.{command}")
            logger.debug(f"명령어 [ {command:^10} ] 로드")

    async def delete_unchecked_guilds(self):
        for music_channel in MusicChannel.get_all():
            if self.get_guild(music_channel.guild_id) is None:
                MusicChannel.delete(music_channel.guild_id)
                logger.debug(f"{music_channel} 삭제됨")
