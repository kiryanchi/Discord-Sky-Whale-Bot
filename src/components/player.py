from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Self

from discord import FFmpegOpusAudio

from setting import FFMPEG_OPTS, TIMER
from src.exception import PlayException
from src.util.function import get_info
from src.util.log import logger

if TYPE_CHECKING:
    from discord import VoiceChannel, VoiceClient

    from src.components.music import Music


class Player:
    def __init__(self, music: Music, channel: VoiceChannel, client: VoiceClient):
        self.music: Music = music
        self.bot = music.bot
        self.channel = channel
        self.guild = channel.guild
        self.client = client
        self.playlist = music.playlist
        self.next = asyncio.Event()

        self.play = asyncio.create_task(self._play())
        logger.info(f"{get_info(self.guild)} Player 생성")

    def __del__(self):
        logger.info(f"{get_info(self.guild)} Player 삭제")

    async def _play(self):
        while True:
            self.next.clear()

            if len(self.channel.members) == 1:
                logger.debug(f"{get_info(self.guild)} 채널에 혼자 있어서 음악 봇 초기화")
                self.bot.loop.create_task(self.stop())
                return

            if not self.music.is_loop:
                try:
                    async with asyncio.timeout(TIMER):
                        song = await self.playlist.next()
                except asyncio.TimeoutError:
                    logger.debug(f"{get_info(self.guild)} 노래 재생 안 해서 음악 봇 초기화")
                    self.bot.loop.create_task(self.stop())
                    return

            logger.info(f"{get_info(self.guild)} 노래 [{song.title}] 재생")
            self.client.play(
                await FFmpegOpusAudio.from_probe(source=song.source, **FFMPEG_OPTS),
                after=self.play_next,
            )

            # 초반 렉 제거
            self.client.pause()
            await asyncio.sleep(0.3)
            self.client.resume()

            await self.next.wait()

    def play_next(self, error=None):
        if error:
            raise PlayException(error)
        logger.debug(f"{get_info(self.guild)} 다음 곡 재생 시그널")
        self.next.set()

    def pause(self):
        if self.client.is_playing():
            logger.debug(f"{get_info(self.guild)} 일시정지")
            self.client.pause()
        else:
            logger.debug(f"{get_info(self.guild)} 재생")
            self.client.resume()
        return self.client.is_paused()

    def skip(self):
        logger.debug(f"{get_info(self.guild)} 노래 스킵")
        self.client.stop()

    async def stop(self):
        if not self.play.done():
            logger.debug(f"{get_info(self.guild)} play가 아직 안 끝났습니다.")
            self.play.cancel()
        if self.client.is_connected():
            logger.debug(f"{get_info(self.guild)} client가 연결되어 있습니다.")
            await self.client.disconnect(force=True)
        await self.playlist.clear()
        await self.music.delete_player()

    @staticmethod
    async def new(music: Music, channel: VoiceChannel) -> Self:
        for voice_client in music.bot.voice_clients:
            if voice_client.channel == channel:
                await voice_client.disconnect(force=True)
        client = await channel.connect()
        return Player(music, channel, client)
