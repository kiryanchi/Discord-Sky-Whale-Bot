from __future__ import annotations

import asyncio
import random
import re
from typing import TYPE_CHECKING, Optional, Self

from discord import Embed

from setting import COLOR, DEFAULT_IMG, QUEUE_SIZE
from src.util.function import get_info
from src.util.log import logger

if TYPE_CHECKING:
    from discord import Message

    from src.components.song import Song


class Playlist:
    def __init__(self, message: Message):
        self.message = message
        self.guild = message.guild
        self.current_song: Optional[Song] = None
        self.next_songs: asyncio.Queue[Song] = asyncio.Queue(QUEUE_SIZE)
        self.current_page: int = 0
        self.max_page: int = 0
        logger.info(f"{get_info(self.guild)} Playlist 생성")

    async def add(self, song: Song):
        if self.next_songs.full():
            return
        await self.next_songs.put(song)
        logger.debug(f"{get_info(self.guild)} 노래 {song.title} 추가")
        if self.current_song:
            await self.update()

    async def next(self) -> Song:
        if self.next_songs.empty():
            logger.debug(f"{get_info(self.guild)} 노래가 없어서 대기")
            self.current_song = None
            await self.update()
        self.current_song = await self.next_songs.get()
        logger.debug(f"{get_info(self.guild)} 노래 {self.current_song.title} 가져옴")
        await self.update()
        return self.current_song

    async def shuffle(self):
        if self.next_songs.empty():
            logger.debug(f"{get_info(self.guild)} 재생목록이 비어있음")
            return
        logger.debug(f"{get_info(self.guild)} 재생목록 셔플")
        random.shuffle(self.next_songs._queue)
        await self.update()

    async def first_page(self):
        if self.current_page != 0:
            logger.debug(f"{get_info(self.guild)} 첫 페이지")
            self.current_page = 0
            await self.update()

    async def prev_page(self):
        if self.current_page > 0:
            logger.debug(f"{get_info(self.guild)} 이전 페이지")
            self.current_page -= 1
            await self.update()

    async def next_page(self):
        if self.current_page < self.max_page:
            logger.debug(f"{get_info(self.guild)} 다음 페이지")
            self.current_page += 1
            await self.update()

    async def last_page(self):
        if self.current_page != self.max_page:
            logger.debug(f"{get_info(self.guild)} 마지막 페이지")
            self.current_page = self.max_page
            await self.update()

    async def clear(self):
        logger.debug(f"{get_info(self.guild)} Playlist 초기화")
        while not self.next_songs.empty():
            song = self.next_songs.get_nowait()
            logger.debug(f"{get_info(self.guild)} 노래 {song.title} 삭제")
            self.next_songs.task_done()
        self.current_song = None
        await self.update()

    async def update(self):
        logger.debug(f"{get_info(self.guild)} Embed 업데이트")
        self.max_page = (
            (self.next_songs.qsize() - 1) // 10 if self.next_songs.qsize() > 0 else 0
        )

        if self.current_page > self.max_page:
            self.current_page = self.max_page

        await self.message.edit(embed=Embed(self))

    @staticmethod
    async def new(message: Message) -> Self:
        player = Playlist(message)
        await player.update()
        return player


class Embed(Embed):
    space = "ㅤ"

    def __init__(self, playlist: Playlist):
        self.playlist = playlist

        super().__init__(title=f" 🐳{self.space}Sky Whale{self.space} 🐳", color=COLOR)
        self.set_image(url=self.current_image).add_field(
            name="현재 재생중인 노래", value=self.current_song_message, inline=False
        ).set_author(
            name="하늘 고래를 서버로 불러보세요!",
            url="https://discord.com/api/oauth2/authorize?client_id=965786057897541682&permissions=8&scope=bot%20applications.commands",
            icon_url=DEFAULT_IMG,
        )
        self.url = "https://discord.gg/T92wcQuznv"

        if self.playlist.current_song:
            self.add_field(
                name="채널",
                value=f"[{self.playlist.current_song.uploader['name']}]({self.playlist.current_song.uploader['link']})",
                inline=False,
            ).add_field(
                name="재생시간",
                value=f"{self.playlist.current_song.duration}",
                inline=True,
            ).add_field(
                name="조회수",
                value=f"{self.playlist.current_song.view_count}",
                inline=True,
            ).add_field(
                name="이거 누가 넣음?",
                value=f"<@{self.playlist.current_song.user.id}>",
                inline=True,
            )

        self.add_field(
            name="대기중인 노래", value=self.next_songs_message, inline=False
        ).set_footer(text="사용법은 도움말 버튼을 눌러보세요")

    @property
    def current_image(self):
        return (
            self.playlist.current_song.thumbnail
            if self.playlist.current_song
            else DEFAULT_IMG
        )

    @property
    def current_song_message(self):
        msg = (
            f"[{self.playlist.current_song.title}]({self.playlist.current_song.link})"
            if self.playlist.current_song
            else "재생중인 노래가 없습니다."
        )
        return msg

    @property
    def next_songs_message(self):
        song_list: list[str] = []

        try:
            for i in range(
                10 * self.playlist.current_page, 10 * (self.playlist.current_page + 1)
            ):
                song_list.append(self.playlist.next_songs._queue[i].title)
        except IndexError:
            empty_song_list = ["예약된 노래가 없습니다." for _ in range(10 - len(song_list))]
            song_list = [*song_list, *empty_song_list]

        msg = ""

        for i in range(len(song_list)):
            tmp = self.wrap(text=song_list[i])
            msg += f"> [{self.playlist.current_page * 10 + i + 1}] {tmp}\n"

        msg += f"> {self.space} \n> {self.space} 현재 페이지 {self.playlist.current_page + 1} / {self.playlist.max_page + 1}"

        return msg

    @staticmethod
    def wrap(text):
        def is_korean(character):
            hangul = re.compile("[^ㄱ-ㅣ가-힣]+")
            result = hangul.sub("", character)
            return result != ""

        word_cnt = 0
        result_text = ""
        for char in text:
            if word_cnt > 42:
                result_text += "..."
                break

            if is_korean(char):
                word_cnt += 2
            else:
                word_cnt += 1

            result_text += char
        return result_text
