import discord
import asyncio
import random

from src.playlist.embed import Embed


class Player:
    INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"

    def __init__(self, bot, playlist_channel, playlist_msg):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.bot = bot
        self._loop = asyncio.get_running_loop()
        self._playing = False
        self._playlist_channel = playlist_channel
        self._playlist_msg = playlist_msg
        self._songs = {"current": None, "next": []}
        self._voice = {"channel": None, "client": None}
        self._page = {"max": 0, "current": 0}

    @property
    def current_page(self):
        return self._page["current"]

    @property
    def max_page(self):
        return self._page["max"]

    @property
    def playlist_msg(self):
        return self._playlist_msg

    @property
    def songs(self):
        return self._songs

    async def first(self, interaction):
        await self._first()
        await interaction.send(
            "처음 페이지",
            delete_after=0.1,
            ephemeral=False,
        )

    async def init(self):
        await self._update_playlist()

    async def last(self, interaction):
        await self._last()
        await interaction.send("마지막 페이지", delete_after=0.1, ephemeral=False)

    async def next(self, interaction):
        await self._next()
        await interaction.send("다음 페이지", delete_after=0.1, ephemeral=False)

    async def pause(self, interaction):
        self._pause()
        await interaction.send(
            f"{interaction.author.name} 님이 일시정지 했습니다.", delete_after=3, ephemeral=False
        )

    async def play(self, message, song):
        if self._voice["client"] is None:
            await self._join(message.author.voice.channel)

        if self._playing:
            await self._add_song(song)
            if not self._same_voice_channel(message.author.voice.channel):
                await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶다면 제가 있는 채널에 들어와주세요!"
                )
            return

        if not self._same_voice_channel(message.author.voice.channel):
            await self._move(message.author.voice.channel)

        await self._play_song(song)

    async def prev(self, interaction):
        await self._prev()
        await interaction.send("이전 페이지", delete_after=0.1, ephemeral=False)

    async def resume(self, interaction):
        self._resume()
        await interaction.send(
            f"{interaction.author.name} 님이 일지정지를 풀었습니다.",
            delete_after=3,
            ephemeral=False,
        )

    async def shuffle(self, interaction):
        self._shuffle()
        await interaction.send(
            f"{interaction.author.name} 님이 재생목록을 흔들었습니다.",
            delete_after=3,
            ephemeral=False,
        )

    async def skip(self, interaction):
        await self._skip()
        await interaction.send(
            f"{interaction.author.name} 님이 노래를 스킵했습니다.", delete_after=3, ephemeral=False
        )

    async def youtube(self, interaction):
        await interaction.send(
            f"Youtbe Link: https://youtu.be/{self._songs['current'].id}"
        )

    async def _add_song(self, song):
        self._songs["next"].append(song)
        await self._update_playlist()

    async def _check_queue(self):
        if not self._songs["next"]:
            self._playing = False
            self._songs["current"] = None
            await self._update_playlist()
            await self._leave()
            return
        if not self._voice["client"] is None:
            await self._play_song(self._get_song())
        # asyncio.run_coroutine_threadsafe(self._play_song(self._get_song()), self._loop)

    async def _first(self):
        if self._page["current"] != 0:
            self._page["current"] = 0
            await self._update_playlist()

    def _get_song(self):
        return self._songs["next"].pop(0)

    async def _join(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await voice_channel.connect()

    async def _last(self):
        if self._page["current"] != self._page["max"]:
            self._page["current"] = self._page["max"]
            await self._update_playlist()

    async def _leave(self):
        self._voice["client"] = await self._voice["client"].disconnect()
        self._voice["channel"] = None

    async def _move(self, voice_channel):
        self._voice["channel"] = voice_channel
        self._voice["client"] = await self.voice["clinet"].move_to(voice_channel)

    async def _next(self):
        if self._page["current"] < self._page["max"]:
            self._page["current"] += 1
            await self._update_playlist()

    def _pause(self):
        if self._voice["client"] and not self._voice["client"].is_paused():
            self._voice["client"].pause()

    async def _play_song(self, song):
        self._playing = True
        self._songs["current"] = song
        await self._update_playlist()

        try:
            self._voice["client"].play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS)
                ),
                after=lambda e: self._loop.create_task(self._check_queue()),
            )
            self._pause()
            await asyncio.sleep(1)
            self._resume()
            print(
                f"[INFO] [{self._playlist_channel.guild.name}] 길드에서 [{self._playlist_channel.name}] 채널에서 [{song.title}] 재생함"
            )
        except discord.opus.OpusNotLoaded:
            print(
                f"[INFO] [{self._playlist_channel.guild.name}] 길드에서 [{self._playlist_channel.name}] 채널에서 [{song.title}] 재생실패함"
            )
            await asyncio.sleep(10)
            await self._check_queue()

    async def _prev(self):
        if self._page["current"] > 0:
            self._page["current"] -= 1
            await self._update_playlist()

    def _resume(self):
        if self._voice["client"] and self._voice["client"].is_paused():
            self._voice["client"].resume()

    def _same_voice_channel(self, voice_channel):
        return self._voice["channel"] == voice_channel

    def _shuffle(self):
        random.shuffle(self._songs["next"])

    async def _skip(self):
        if self._voice["client"] is None:
            print("skip 할게 없음")
            return
        if self._playing:
            print("skip")
            self._voice["client"].stop()

    async def _update_playlist(self):
        self._page["max"] = len(self._songs["next"]) // 10
        if self._page["current"] > self._page["max"]:
            self._page["current"] = self._page["max"]

        embed, components = Embed.playlist(self)

        await self._playlist_msg.edit(embed=embed, components=components)
