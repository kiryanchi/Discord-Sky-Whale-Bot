from __future__ import annotations

import glob
import platform
from itertools import cycle
from typing import Dict
from typing import TYPE_CHECKING

from discord import Game, Intents, Object, Guild, opus
from discord.ext import commands, tasks

from setting import COMMANDS, DEBUG, DEFAULT_PREFIX, ADMIN_GUILD_ID
from src.model.music_channel import MusicChannel
from src.tools import logger

if TYPE_CHECKING:
    from src.cogs.music.components import Player

GAME_LIST = cycle(["향유", "유튜브 검색", "넷플릭스"])

ADMIN_GUILD = Object(id=ADMIN_GUILD_ID)


class Whale(commands.Bot):
    players: Dict[int, Player] = {}

    def __init__(self):
        super().__init__(intents=Intents.all(), command_prefix=DEFAULT_PREFIX)

    async def setup_hook(self) -> None:

        logger.info("opus 로드 확인")
        if platform.system() == "Darwin":
            logger.debug("opus 확인 불가. 다시 불러옵니다.")
            _opus = glob.glob("/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib")
            opus.load_opus(_opus[0])
        logger.info("opus 로드 완료")

        logger.info(f"명령어 로드 시작")
        for command in COMMANDS:
            await self.load_extension(f"src.cogs.{command}.{command}")
            logger.info(f"명령어 [ {command:^10} ] 로드")
        logger.info(f"명령어 로드 완료")

        if DEBUG:
            self.tree.copy_global_to(guild=ADMIN_GUILD)
        await self.tree.sync(guild=ADMIN_GUILD if DEBUG else None)
        logger.info(f"{'길드' if DEBUG else '서버'} 명령어 등록 완료")

    async def on_ready(self):
        logger.info("DB에서 확인되지 않은 길드 삭제하는 중")
        for music_channel in MusicChannel.get_all():
            if self.get_guild(music_channel.guild_id) is None:
                MusicChannel.delete(music_channel.guild_id)
                logger.debug(f"{music_channel} 삭제됨")
        logger.info("DB 정리 완료")

        logger.info(f"{self.user} 로그인 성공")

        @tasks.loop(minutes=30)
        async def change_game():
            current_game = next(GAME_LIST)
            await self.change_presence(activity=Game(current_game))
            # log.info(f"{current_game} 하는 중")

        change_game.start()

    async def on_guild_remove(self, guild: Guild):
        # TODO: 길드 나가면 데이터베이스에서 삭제
        return
