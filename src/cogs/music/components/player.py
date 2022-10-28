from __future__ import annotations

import asyncio
import random
from typing import List, Optional, TYPE_CHECKING

from discord import (
    Message,
    PCMVolumeTransformer,
    FFmpegPCMAudio,
    Interaction,
    VoiceClient,
    TextChannel,
    Member,
)

from src.cogs.music.view import PlaylistEmbed, PlaylistView, HelpEmbed
from src.tools import logger
from src.whale import Whale

if TYPE_CHECKING:
    from src.cogs.music.components import Song

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Player:
    def __init__(self, bot: Whale, playlist: Message):
        self.bot = bot
        self.playlist = playlist
        self.guild = playlist.guild
        self.channel = playlist.channel
        self.playing = False
        self.loop = asyncio.get_running_loop()
        self._songs = {"current": None, "next": []}
        self._voice = {"channel": None, "client": None}
        self._page = {"current": 0, "max": 0}

    @property
    def current_song(self) -> Optional[Song]:
        return self._songs["current"]

    @current_song.setter
    def current_song(self, value):
        self._songs["current"] = value

    @property
    def next_songs(self) -> List[Optional[Song]]:
        return self._songs["next"]

    @property
    def current_page(self) -> int:
        return self._page["current"]

    @current_page.setter
    def current_page(self, value):
        self._page["current"] = value

    @property
    def max_page(self) -> int:
        return self._page["max"]

    @max_page.setter
    def max_page(self, value):
        self._page["max"] = value

    async def join(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await voice_channel.connect()

    async def leave(self):
        if self._voice["client"]:
            await self._voice["client"].disconnect()

        self._voice["client"] = None
        self._voice["channel"] = None

    async def pause(self, interaction: Interaction = None):
        self._voice["client"]: VoiceClient
        if self._voice["client"] and self._voice["client"].is_playing():
            self._voice["client"].pause()
        if interaction:
            await interaction.response.send_message(
                f"{interaction.user.name}님이 일시정지 했습니다."
            )
            await asyncio.sleep(1)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 일시정지"
            )

    async def resume(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(
                f"{interaction.user.name}님이 일시정지를 풀었습니다."
            )
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 일시정지 해제"
            )
        if self._voice["client"] and self._voice["client"].is_paused():
            self._voice["client"].resume()

    async def skip(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(
                f"{interaction.user.name}님이 노래를 스킵했습니다."
            )
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 스킵"
            )

        if self.playing:
            self._voice["client"].stop()

    async def shuffle(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(
                f"{interaction.user.name}님이 재생목록을 흔들었습니다."
            )
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 셔플"
            )
        random.shuffle(self.next_songs)
        await self.update_playlist()

    async def help(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.defer(thinking=True, ephemeral=True)
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 help"
            )
        help_embed = HelpEmbed()
        await interaction.edit_original_response(embed=help_embed)

    async def first(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(f"재생목록 첫 페이지")
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 first"
            )
        if self.current_page != 0:
            self.current_page = 0
            await self.update_playlist()

    async def prev(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(f"재생목록 이전 페이지")
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 prev"
            )
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_playlist()

    async def next(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(f"재생목록 다음 페이지")
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 next"
            )
        if self.current_page < self.max_page:
            self.current_page += 1
            await self.update_playlist()

    async def last(self, interaction: Interaction = None):
        if interaction:
            await interaction.response.send_message(f"재생목록 마지막 페이지")
            await asyncio.sleep(3)
            await interaction.delete_original_response()
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 last"
            )
        if self.current_page != self.max_page:
            self.current_page = self.max_page
            await self.update_playlist()

    async def youtube(self, interaction: Interaction = None):
        if self.current_song:
            await interaction.response.send_message(
                f"현재 재생 중인 노래: {self.current_song.webpage_url}", ephemeral=True
            )
            logger.debug(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.user.name} 봇 youtube"
            )

    async def play(self, channel: TextChannel, song: Song, author: Member):

        # TODO: 이거 왠지 위차 바꾸면 최적화 가능할 것 같은데
        if self._voice["client"] is None:
            await self.join(author.voice.channel)

        await self._add_song(song)
        if self.playing:
            if not self._same_voice_channel(author.voice.channel):
                await channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶다면 제가 있는 채널에 들어와주세요!",
                    delete_after=5,
                )
            return

        if not self._same_voice_channel(author.voice.channel):
            await self._move(author.voice.channel)

        await self._check_queue()
        # await self._play(song)

    async def _add_song(self, song: Song):
        self.next_songs.append(song)
        await self.update_playlist()

    async def _play(self, song: Song):
        self.playing = True
        await self.update_playlist()

        logger.info(f"길드: [{self.guild.id}/{self.guild.name}] :: {song.title} 재생")
        self._voice["client"].play(
            PCMVolumeTransformer(FFmpegPCMAudio(song.url, **FFMPEG_OPTIONS)),
            after=lambda e: self.loop.create_task(self._check_queue()),
        )
        await self.pause()
        await asyncio.sleep(1)
        await self.resume()

    async def _move(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await self._voice["client"].move_to(voice_channel)

    async def _check_queue(self):
        if not self.next_songs:
            self.playing = False
            self.current_song = None
            await self.update_playlist()
            await self.leave()
            return

        self.current_song = self.next_songs.pop()
        await self._play(self.current_song)

    async def update_playlist(self):
        self.max_page = (
            (len(self.next_songs) - 1) // 10 if len(self.next_songs) > 0 else 0
        )

        if self.current_page > self.max_page:
            self.current_page = self.max_page

        embed = PlaylistEmbed(self)
        view = PlaylistView(self)

        await self.playlist.edit(embed=embed, view=view)

    def _same_voice_channel(self, voice_channel):
        return self._voice["channel"] == voice_channel
