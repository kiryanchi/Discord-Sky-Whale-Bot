from itertools import cycle

from discord import Game, Intents, Object
from discord.ext import commands, tasks

from setting import COMMANDS
from src.tools import Env, set_logger

log = set_logger()
GAME_LIST = cycle(["향유", "유튜브 검색", "넷플릭스"])

ADMIN_GUILD = Object(id=750959484477898873)


class Whale(commands.Bot):
    def __init__(self, prefix: str, env: Env):
        super().__init__(intents=Intents.all(), command_prefix=prefix)
        self.env = env
        self.players = {}

    async def setup_hook(self) -> None:
        for command in COMMANDS:
            cog = f"src.cogs.{command}.command"
            log.info(f"Cog [ {cog[9:]:^10} ] 로드 완료")
            await self.load_extension(cog)

        if self.env.environment == "dev":
            self.tree.copy_global_to(guild=ADMIN_GUILD)
        await self.tree.sync(
            guild=ADMIN_GUILD if self.env.environment == "dev" else None
        )
        log.info(
            f"현재 개발 환경: {self.env.environment}, {'길드' if self.env.environment == 'dev' else '서버'} 명령어 등록 완료"
        )

    async def on_ready(self):
        log.info(f"{self.user} 로그인 성공")

        @tasks.loop(minutes=30)
        async def change_game():
            current_game = next(GAME_LIST)
            await self.change_presence(activity=Game(current_game))
            # log.info(f"{current_game} 하는 중")

        change_game.start()
