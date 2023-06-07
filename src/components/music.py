from __future__ import annotations

from typing import TYPE_CHECKING, Self, Optional

from discord import ui, ButtonStyle

from setting import INIT_MSG
from src.components.player import Player
from src.components.playlist import Playlist
from src.embeds.help import Help
from src.util.function import get_info
from src.util.log import logger

if TYPE_CHECKING:
    from discord import TextChannel, Interaction, User, Message

    from src.extended_bot import ExtendedBot
    from src.components.song import Song


class Music:
    def __init__(
        self,
        bot: ExtendedBot,
        channel: TextChannel,
        message: Message,
        playlist: Playlist,
    ):
        self.bot = bot
        self.channel = channel
        self.guild = channel.guild
        self.message = message
        self.playlist = playlist
        self.player: Optional[Player] = None
        self._loop = False
        logger.info(f"{get_info(channel.guild)} Music 생성")

    @property
    def is_playing(self):
        if self.player:
            return self.player.client.is_paused()
        return False

    @property
    def is_loop(self):
        return self._loop

    async def play(self, song: Song, user: User):
        await self.playlist.add(song)

        if self.player is None:
            self.player = await Player.new(self, user.voice.channel)

    async def delete_player(self):
        if self.player:
            del self.player
            self.player = None
            logger.debug(f"{get_info(self.guild)} Player 삭제")
        await self.update()

    async def pause(self, interaction: Interaction):
        if self.is_playing:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 재생 했습니다.", delete_after=3, silent=True
            )
            logger.info(f"{get_info(self.guild)} 노래 일시정지 해제")
        else:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 일시정지 했습니다.", delete_after=3, silent=True
            )
            logger.info(f"{get_info(self.guild)} 노래 일시정지")
        if self.player:
            self.player.pause()
            await self.update()

    async def skip(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Skip Interaction")
        if self.is_loop:
            await interaction.response.send_message(
                "`스킵`을 하려면 `반복`을 해제해주세요", delete_after=5, silent=True
            )
        else:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 노래를 `스킵`했습니다.", delete_after=3, silent=True
            )
            logger.info(f"{get_info(self.guild)} 노래 스킵")
            if self.player:
                self.player.skip()

    async def shuffle(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Shuffle Interaction")
        logger.info(f"{get_info(self.guild)} 재생 목록을 흔듦")
        await interaction.response.send_message(
            f"<@{interaction.user.id}> 님이 재생목록을 흔들었습니다.", delete_after=3, silent=True
        )
        await self.playlist.shuffle()

    async def reset(self, interaction: Interaction = None):
        logger.debug(f"{get_info(self.guild)} Reset Interaction")
        logger.info(f"{get_info(self.guild)} 하늘고래 초기화")
        if interaction:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 하늘 고래를 죽였습니다...", delete_after=5, silent=True
            )
        self._loop = False
        if self.player:
            self.bot.loop.create_task(self.player.stop())
            await self.delete_player()
        else:
            await self.playlist.clear()
        await self.channel.purge(after=self.playlist.message)

    async def help(self, interaction: Interaction = None):
        logger.info(f"{get_info(self.guild)} 도움말 요청")
        if interaction:
            await interaction.response.defer(thinking=True, ephemeral=True)
            await interaction.edit_original_response(embed=Help())

    async def first(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} First Interaction")
        await interaction.response.defer(thinking=True)
        await self.playlist.first_page()
        await interaction.delete_original_response()

    async def prev(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Prev Interaction")
        await interaction.response.defer(thinking=True)
        await self.playlist.prev_page()
        await interaction.delete_original_response()

    async def next(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Next Interaction")
        await interaction.response.defer(thinking=True)
        await self.playlist.next_page()
        await interaction.delete_original_response()

    async def last(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Last Interaction")
        await interaction.response.defer(thinking=True)
        await self.playlist.last_page()
        await interaction.delete_original_response()

    async def loop(self, interaction: Interaction):
        logger.debug(f"{get_info(self.guild)} Loop Interaction")
        if self.is_loop:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 반복을 해제했습니다.", delete_after=3, silent=True
            )
            logger.info(f"{get_info(self.guild)} 노래 반복 해제")
        else:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> 님이 반복을 설정했습니다.", delete_after=3, silent=True
            )
            logger.info(f"{get_info(self.guild)} 노래 반복 설정")
        if self.player:
            logger.debug(f"{get_info(self.guild)} 한곡 반복 설정")
            self._loop = not self._loop
            await self.update()
            await interaction.delete_original_response()

    async def update(self):
        logger.debug(f"{get_info(self.guild)} View 업데이트")
        view = View(self)
        await self.message.edit(view=view)

    @staticmethod
    async def new(bot: ExtendedBot, channel: TextChannel) -> Self:
        await channel.purge()
        message = await channel.send(content=INIT_MSG, silent=True)
        playlist = await Playlist.new(message)
        music = Music(bot, channel, message, playlist)
        await message.edit(view=View(music))
        return music


class View(ui.View):
    def __init__(self, music: Music):
        super().__init__(timeout=None)
        self.music = music

        components_list = [
            [
                Button(style=ButtonStyle.green, label="재생", custom_id="pause", row=0)
                if self.music.is_playing
                else Button(
                    style=ButtonStyle.red, label="일시정지", custom_id="pause", row=0
                ),
                Button(style=ButtonStyle.blurple, label="스킵", custom_id="skip", row=0),
                Button(style=ButtonStyle.grey, label="셔플", custom_id="shuffle", row=0),
                Button(style=ButtonStyle.green, label="반복끄기", custom_id="loop", row=0)
                if self.music.is_loop
                else Button(
                    style=ButtonStyle.grey, label="반복켜기", custom_id="loop", row=0
                ),
                Button(style=ButtonStyle.grey, label="도움말", custom_id="help", row=0),
            ],
            [
                Button(style=ButtonStyle.grey, label="<<", custom_id="first", row=1),
                Button(style=ButtonStyle.grey, label="<", custom_id="prev", row=1),
                Button(style=ButtonStyle.grey, label=">", custom_id="next", row=1),
                Button(style=ButtonStyle.grey, label=">>", custom_id="last", row=1),
                Button(style=ButtonStyle.red, label="초기화", custom_id="reset", row=1),
            ],
        ]

        for components in components_list:
            for button in components:
                self.add_item(button)


class Button(ui.Button[View]):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, row: int):
        super().__init__(style=style, custom_id=custom_id, label=label, row=row)

    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None

        actions = {
            "pause": self.view.music.pause,
            "skip": self.view.music.skip,
            "shuffle": self.view.music.shuffle,
            "reset": self.view.music.reset,
            "help": self.view.music.help,
            "first": self.view.music.first,
            "prev": self.view.music.prev,
            "next": self.view.music.next,
            "last": self.view.music.last,
            "loop": self.view.music.loop,
        }

        await actions[self.custom_id](interaction)
