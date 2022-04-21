import discord
import asyncio
import random


class Player:
    def __init__(self, playlist_channel):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self._loop = asyncio.get_running_loop()
        self._playing = False
        self.playlist_channel = playlist_channel
        self._playlist_msg = None
        self._songs = {"current": None, "next": []}
        self._voice = {"channel": None, "client": None, "source": None}

    @property
    def playlist_msg(self):
        return self._playlist_msg

    def set_playlist_msg(self, msg):
        self._playlist_msg = msg

    def pause(self):
        if self._voice["client"] and not self._voice["client"].is_paused():
            self._voice["client"].pause()

    def resume(self):
        if self._voice["client"] and self._voice["client"].is_paused():
            self._voice["client"].resume()

    async def skip(self):
        if self._voice["client"] is None:
            print("skip 할게 없음")
            return
        if self._playing:
            print("skip")
            self._voice["client"].stop()

    async def play(self, message, song):
        if self._voice["client"] is None:
            await self._join(message.author.voice.channel)

        if self._playing:
            self._add_song(song)
            if not self._same_voice_channel(message.author.voice.channel):
                await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶다면 제가 있는 채널에 들어와주세요!"
                )
            return

        if not self._same_voice_channel(message.author.voice.channel):
            await self._move(message.author.voice.channel)

        await self._play_song(song)

    def _add_song(self, song):
        self._songs["next"].append(song)

    async def _check_queue(self):
        print("[DEBUG] _check_queue")
        if not self._songs["next"]:
            self._playing = False
            self._songs["current"] = None
            await self._leave()
            return
        if not self._voice["client"] is None:
            await self._play_song(self._get_song())
        # asyncio.run_coroutine_threadsafe(self._play_song(self._get_song()), self._loop)

    def _get_song(self):
        return self._songs["next"].pop(0)

    async def _join(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await voice_channel.connect()

    async def _leave(self):
        self._voice["client"] = await self._voice["client"].disconnect()
        self._voice["channel"] = None

    async def _move(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await self.voice["clinet"].move_to(voice_channel)

    async def _play_song(self, song):
        self._playing = True
        self._songs["current"] = song

        try:
            self._voice["source"] = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS)
            )
            self._voice["source"].volume = 0.1

            self._voice["client"].play(
                self._voice["source"],
                after=lambda e: self._loop.create_task(self._check_queue()),
            )
            self.pause()
            await asyncio.sleep(1)
            self.resume()
            print(
                f"[INFO] [{self.playlist_channel.guild.name}] 길드에서 [{self.playlist_channel.name}] 채널에서 [{song.title}] 재생함"
            )
        except discord.opus.OpusNotLoaded:
            print(
                f"[INFO] [{self.playlist_channel.guild.name}] 길드에서 [{self.playlist_channel.name}] 채널에서 [{song.title}] 재생실패함"
            )
            await asyncio.sleep(10)
            await self._check_queue()

    def _same_voice_channel(self, voice_channel):
        return self._voice["channel"] == voice_channel

    def _shuffle(self):
        random.shuffle(self._songs["next"])
