import discord


class Playlist:
    def __init__(self, channel, playlist_msg):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.channel = channel
        self.playlist_msg = playlist_msg
        self.voice_channel = None
        self.voice_client = None
        self.queue = {
            "prev_song": None,
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

    def add_next_song(self, song):
        self.queue["next_songs"].append(song)

    def get_prev_song(self):
        return self.queue["prev_song"]

    def set_prev_song(self, song):
        self.queue["prev_song"] = song

    def is_same_voice_channel(self, channel):
        return self.voice_channel == channel

    def reset_voice_status(self):
        self.voice_channel = None
        self.voice_client = None

    async def join(self, channel):
        self.voice_channel = channel
        self.voice_client = await self.voice_channel.connect()

    async def move(self, channel):
        self.voice_channel = channel
        await self.voice_client.move_to(self.voice_channel)

    async def _check_queue(self, song):
        self.set_prev_song(song)
        if len(self.song_queue) == 0:
            self.playing = False
            return
        self.voice_client.stop()
        await self._play_song()

    async def _play_song(self):
        song = self.get_next_song()
        self.playing = True
        self.voice_client.play(
            discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song.mp3, **self.FFMPEG_OPTIONS)
            ),
            after=lambda error: self.app.loop.create_task(self._check_queue(song)),
        )

    async def play(self, message, song):
        self.add_next_song(song)
        # 음성 채널에 연결되어 있지 않다면, 음성 채널에 입장
        if self.voice_client is None:
            await self.join(message.author.voice.channel)

        # 노래를 재생 중이 아니라면,
        if self.playing is False:
            if not self.is_same_voice_channel(message.author.voice.channel):
                await self.move(message.author.voice.channel)
            await self._play_song()

        # 노래를 재생 중이라면,
        else:
            if not self.is_same_voice_channel(message.author.voice.channel):
                await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶으면 제 음성 채널에 들어와주세요!",
                    delete_after=3,
                )
