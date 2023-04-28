from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import Embed, ui, ButtonStyle
from youtubesearchpython.__future__ import VideosSearch

from setting import NUM_OF_SEARCH, COLOR, DEFAULT_IMG
from src.exception import NoResultException

if TYPE_CHECKING:
    from discord import User, Interaction
    from src.extended_bot import ExtendedBot


class Search:
    def __init__(self, bot: ExtendedBot):
        self.bot = bot

    @staticmethod
    async def from_youtube(title: str):
        result: Optional[list]
        if result := (
            await VideosSearch(
                query=title, limit=NUM_OF_SEARCH, language="kr", region="KR"
            ).next()
        ).get("result", None):
            return result
        raise NoResultException(f"유튜브 검색 결과가 없습니다: {title}")

    @staticmethod
    def make_ui(title: str, user: User, searches):
        embed = Embed(title, user, searches)
        view = View(user, searches)

        return embed, view


class Embed(Embed):
    def __init__(self, title: str, user: User, searches: list):
        super().__init__(
            title=f"{title} 검색 결과",
            description=f"<@{user.id}> 검색",
            color=COLOR,
        )
        self.set_thumbnail(url=DEFAULT_IMG)

        for i in range(len(searches)):
            search = searches[i]
            self.add_field(
                name=f"{i + 1:2d}번\t({search['duration']}) {search['channel']['name']}",
                value=f"제목: {search['title']}",
                inline=False,
            )


class View(ui.View):
    def __init__(self, user: User, searches: list):
        super().__init__(timeout=15)
        self.searches = searches
        self.user = user
        self.link: str = ""

        for i in range(NUM_OF_SEARCH // 5 + 1):
            for j in range(1, 6):
                if i * 5 + j - 1 < NUM_OF_SEARCH:
                    self.add_item(Button(label=str(i * 5 + j), row=i))


class Button(ui.Button[View]):
    def __init__(self, label: str, row: int):
        super().__init__(style=ButtonStyle.secondary, label=label, row=row)

    async def callback(self, interaction: Interaction):
        assert self.view is not None

        if interaction.user != self.view.user:
            await interaction.response.send_message(
                content="쉿! 신청자만 선택할 수 있어요...!", ephemeral=True, delete_after=5
            )
        else:
            self.view.link = self.view.searches[int(self.label) - 1]["link"]
            self.view.stop()
