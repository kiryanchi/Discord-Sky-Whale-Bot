import discord
import asyncio
import random

from src.utils.components import Components
from src.utils.embeds import Embed

SPACE = "\u17B5"


class Playlist:
    def __init__(self, app, channel, playlist_msg):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.app = app
        self.channel = channel
        self.playlist_msg = playlist_msg
        self.voice_channel = None
        self.voice_client = None
        self.queue = {
            "current_song": None,
            "next_songs": [],
        }
        self.playing = False
        self.current_page = 0
        self.max_page = 0

    def pause(self):
        if self.voice_client is None:
            return
        if not self.voice_client.is_paused():
            self.voice_client.pause()

    def resume(self):
        if self.voice_client is None:
            return
        if self.voice_client.is_paused():
            self.voice_client.resume()

    async def shuffle(self):
        if len(self.get_next_songs()) == 0:
            return
        random.shuffle(self.queue["next_songs"])
        await self.update_playlist()

    async def help(self):
        pass

    async def skip(self):
        if self.voice_client is None:
            return
        if self.playing:
            self.voice_client.stop()
            await self._check_queue()

    async def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_playlist()

    async def next_page(self):
        if self.current_page < self.max_page:
            self.current_page += 1
            await self.update_playlist()

    async def first_page(self):
        if self.current_page != 0:
            self.current_page = 0
            await self.update_playlist()

    async def last_page(self):
        if self.current_page != self.max_page:
            self.current_page = self.max_page
            await self.update_playlist()

    async def youtube(self):
        pass

    def get_channel_id(self):
        return self.channel.id

    def get_current_song(self):
        return self.queue["current_song"]

    def set_current_song(self, song):
        self.queue["current_song"] = song

    def get_next_songs(self):
        return self.queue["next_songs"]

    def get_next_song(self):
        return self.queue["next_songs"].pop(0)

    async def update_playlist(self):
        self.max_page = len(self.get_next_songs()) // 10
        if self.current_page > self.max_page:
            self.current_page = self.max_page
        await self._update_playlist_message()

    async def _update_playlist_message(self):
        current_song_message = self._make_current_song_embed_message()
        next_songs_message = self._make_next_songs_embed_message()
        await self.playlist_msg.edit(
            embed=Embed.playlist(current_song_message, next_songs_message),
            components=Components.playlist(self.app),
        )

    def _make_current_song_embed_message(self):
        if (song := self.get_current_song()) is None:
            return "재생중인 노래가 없습니다."
        return song.title

    def _make_next_songs_embed_message(self):
        next_song_list = self.get_next_songs()
        song_list = []
        try:
            for i in range(10 * self.current_page, 10 * (self.current_page + 1)):
                song_list.append(next_song_list[i].title)
        except IndexError:
            # 노래가 10개 이하라면 IndexError 발생
            pass
        append_song_list = []
        # 예약된 곡이 10곡 이하라면 남은 공간에 재생목록이 비어있다고 표시
        if len(song_list) < 10:
            append_song_list = ["예약된 노래가 없습니다." for i in range(10 - len(song_list))]

        song_list = [*song_list, *append_song_list]
        text = ""
        for i in range(len(song_list)):
            tmp = Embed.wrap(song_list[i])
            text += f"> {SPACE}[{self.current_page * 10 + i + 1}] {tmp}\n"
        text += f"> {SPACE}{SPACE}{SPACE}{SPACE}\n"
        text += f"> {SPACE} 현재 페이지 {self.current_page + 1} / {self.max_page + 1}"
        return text

    def add_next_song(self, song):
        self.queue["next_songs"].append(song)

    def is_same_voice_channel(self, voice_channel):
        return self.voice_channel == voice_channel

    def reset_voice_status(self):
        self.voice_channel = None
        self.voice_client = None
        self.playing = False
        self.set_current_song(None)

    async def join(self, voice_channel):
        self.voice_channel = voice_channel
        self.voice_client = await self.voice_channel.connect()

    async def move(self, voice_channel):
        self.voice_channel = voice_channel
        await self.voice_client.move_to(self.voice_channel)

    async def leave(self):
        await self.voice_client.disconnect()
        self.reset_voice_status()

    async def _check_queue(self):
        if not self.get_next_songs():
            await self.leave()
            await self.update_playlist()
            return
        self.voice_client.stop()
        await self._play_song()

    async def _play_song(self):
        song = self.get_next_song()
        self.set_current_song(song)
        self.playing = True
        await self.update_playlist()
        try:
            self.voice_client.play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song.mp3, **self.FFMPEG_OPTIONS)
                ),
                after=lambda error: self.app.loop.create_task(self._check_queue()),
            )
        except discord.opus.OpusNotLoaded:
            await asyncio.sleep(20)
            print(f"{song.title} played")
            await self._check_queue()

        # DELETE
        # await asyncio.sleep(30)
        # await self._check_queue()
        # // DELETE

    async def play(self, message, song):
        # 노래를 추가한다
        self.add_next_song(song)

        # 음성 채널에 연결되어 있지 않다면, 음성 채널에 입장
        if self.voice_client is None:
            await self.join(message.author.voice.channel)

        # 노래를 재생 중이 아니라면,
        if self.playing is False:
            if not self.is_same_voice_channel(message.author.voice.channel):
                await self.move(message.author.voice.channel)
            await self._check_queue()

        # 노래를 재생 중이라면,
        else:
            await self.update_playlist()
            if not self.is_same_voice_channel(message.author.voice.channel):
                await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶으면 제 음성 채널에 들어와주세요!",
                    delete_after=3,
                )
