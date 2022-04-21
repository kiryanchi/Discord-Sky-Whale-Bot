import re
import discord
import asyncio
import random
from discord.ext import commands

from src.playlist.embed import Embed
from src.playlist.song import Song
from src.playlist.youtube import Youtube



class Player:
    def __init__(self, loop, playlist_channel):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self._loop = loop
        self._playing = False
        self.playlist_channel = playlist_channel
        self._playlist_msg = None
        self._songs = {"current": None, "next": []}
        self._voice = {"channel": None, "client": None}

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
            print('skip 할게 없음')
            return
        if self._playing:
            print('skip')

            await self._check_queue()

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
        if not self._songs["next"]:
            self._playing = False
            self._songs["current"] = None
            await self._leave()
            return
        self._voice["client"].stop()
        await self._play_song(self._get_song())

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
            self._voice["client"].play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS)
                ),
                after=lambda error: asyncio.run_coroutine_threadsafe(self._check_queue(), self._loop),
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


class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.players = {}

    @commands.Cog.listener()
    async def on_ready(self):
        servers = self.db.select_all_music_channel()
        if servers:
            for guild_id, channel_id in servers:
                channel = self.bot.get_channel(channel_id)
                await self._create_playlist(channel)
        print("[INFO] 음악봇 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.channel not in self.bot.music_channel_list:
            return

        if message.content == f"{self.bot.command_prefix}초기화":
            await self.bot.process_command(message)
            return

        if message.content.startswith(self.bot.command_prefix):
            return

        if message.author.voice is None:
            await message.channel.send("음성 채널에 들어가서 사용해주세요", delete_after=3)
            await asyncio.sleep(3)
            await message.delete()
            return

        if "list=" in message.content:
            return await message.channel.send("재생목록은 넣을 수 없습니다.", delete_after=3)

        if not self._check_youtube_link(message.content):
            link = await self._select_youtube_link(message)
        else:
            link = message.content

        await self.players[message.guild].play(
            message=message, song=Youtube.extract_info(link=link)
        )

        await message.delete()

    @commands.command(name="초기화", help="이 채널을 음악봇이 사용합니다.")
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        async def callback(interaction):
            if interaction.user == ctx.author:
                if self.db.select_music_channel(ctx.guild.id):
                    self.db.delete_music_channel(ctx.guild.id)
                self.db.insert_music_channel(ctx.guild.id, ctx.channel.id)
            await self._create_playlist(ctx.channel)

        embed, components = Embed.start()
        components = [
            self.bot.components_manager.add_callback(component, callback)
            for component in components
        ]

        await ctx.send(embed=embed, components=components, delete_after=5)

    def _check_youtube_link(self, link):
        if "youtube.com" in link or "youtu.be" in link:
            return True

    async def _create_playlist(self, channel):
        async def callback(interaction):
            actions = {
                "pause": self._pause,
                "resume": self._resume,
                "shuffle": self._shuffle,
                "skip": self._skip,
                "prev": self._prev,
                "next": self._next,
                "first": self._first,
                "last": self._last,
            }
            await actions[interaction.custom_id](interaction)

        await channel.purge()

        embed, components_list = Embed.playlist()

        components = [
            [
                self.bot.components_manager.add_callback(component, callback)
                for component in components
            ]
            for components in components_list
        ]

        if channel in self.bot.music_channel_list:
            self.bot.music_channel_list.remove(channel)
        self.bot.music_channel_list.append(channel)

        player = Player(loop=self.bot.loop, playlist_channel=channel)
        playlist_msg = await channel.send(embed=embed, components=components)
        player.set_playlist_msg(playlist_msg)
        self.players[channel.guild] = player

        print(f"[INFO] [{channel.guild.name}] 길드 [{channel.name}] 채널 음악 봇 초기화 완료")

    async def _first(self, interaction):
        pass

    async def _next(self, interaction):
        pass

    async def _last(self, interaction):
        pass

    async def _pause(self, interaction):
        self.players[interaction.guild].pause()
        await interaction.send(
            f"{interaction.author.name} 님이 일시정지 했습니다.", delete_after=3, ephemeral=False
        )

    async def _prev(self, interaction):
        pass

    async def _resume(self, interaction):
        self.players[interaction.guild].resume()
        await interaction.send(
            f"{interaction.author.name} 님이 일지정지를 풀었습니다.",
            delete_after=3,
            ephemeral=False,
        )

    async def _select_youtube_link(self, message):
        result = await Youtube.search(title=message.content)
        embed, components = Embed.search(message.content, result)

        # 유튜브 검색 후 9개 뽑아옴

        select_message = await message.channel.send(embed=embed, components=components)

        try:
            res = await self.bot.wait_for(
                "button_click",
                check=(
                    lambda interaction: message.author == interaction.user
                    and message.content in interaction.custom_id
                ),
                timeout=15,
            )
            select = res.component.label
            if select == "Cancel":
                raise asyncio.exceptions.TimeoutError
            else:
                select = int(select)

        except asyncio.exceptions.TimeoutError:
            await select_message.delete()
            await message.channel.send("노래 선택이 취소되었습니다.", delete_after=5)
            return

        await select_message.delete()

        link = f"https://youtu.be/{result[select - 1]['id']}"

        return link

    async def _shuffle(self, interaction):
        self.players[interaction.guild].shuffle()
        await interaction.send(
            f"{interaction.author.name} 님이 재생목록을 흔들었습니다.",
            delete_after=3,
            ephemeral=False,
        )

    async def _skip(self, interaction):
        await self.players[interaction.guild].skip()
        await interaction.send(
            f"{interaction.author.name} 님이 노래를 스킵했습니다.", delete_after=3, ephemeral=False
        )


def setup(bot):
    bot.add_cog(Playlist(bot))
