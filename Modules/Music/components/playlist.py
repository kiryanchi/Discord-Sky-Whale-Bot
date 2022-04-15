import discord
import asyncio

from Modules.Music.utils.components import Components
from Modules.Music.utils.embeds import Embed


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

    async def update_playlist_message(self):
        current_song_message = self._make_current_song_embed_message()
        next_songs_message = self._make_next_songs_embed_message()
        await self.playlist_msg.edit(
            embed=Embed.playlist(current_song_message, next_songs_message),
            components=Components.playlist(),
        )

    def _make_current_song_embed_message(self):
        if (song := self.get_current_song()) is None:
            return "비어 있어요"
        return song.title

    def _make_next_songs_embed_message(self):
        next_songs = self.get_next_songs()
        if len(next_songs) == 0:
            return "비어 있ㄴ요"

        text = ""
        for idx in range(len(next_songs)):
            text += f"[{idx + 1}] {next_songs[idx].title}\n"

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
            await self.update_playlist_message()
            return
        self.voice_client.stop()
        await self._play_song()

    async def _play_song(self):
        song = self.get_next_song()
        self.set_current_song(song)
        self.playing = True
        await self.update_playlist_message()
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
            await self.update_playlist_message()
            if not self.is_same_voice_channel(message.author.voice.channel):
                await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶으면 제 음성 채널에 들어와주세요!",
                    delete_after=3,
                )
