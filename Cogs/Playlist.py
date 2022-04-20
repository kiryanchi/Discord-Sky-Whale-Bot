import re
import discord
import asyncio
from discord.ext import commands

from discord_components import Button, ButtonStyle


# Class Youtube
import youtube_dl
from youtubesearchpython import VideosSearch


# Embed Constant
COLOR = 0x8AFDFD
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"
CURRENT_SONG_NAME: str = "현재 재생중인 노래"
NEXT_SONGS_NAME: str = "대기중인 노래"

INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"
NUM_OF_SEARCH = 9


class Embed:
    def wrap(self, text):
        def is_korean(char):
            hangul = re.compile("[^ㄱ-ㅣ가-힣]+")
            result = hangul.sub("", char)
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

    @staticmethod
    def start():
        embed = (
            discord.Embed(title="하늘 고래가 이 곳을 떠다니고 싶어합니다.", color=COLOR)
            .set_image(url=URL)
            .set_footer(text="수락을 누르면 이 채널을 음악 채널로 사용합니다.")
        )

        components = [
            Button(style=ButtonStyle.green, label="여기에 날아다니렴", custom_id="fly")
        ]

        return embed, components

    @staticmethod
    def search(title, search):
        NUM_OF_SEARCH = 9
        embed = discord.Embed(title=f"{title} 검색 결과", color=COLOR).set_thumbnail(
            url=URL
        )

        for i in range(len(search)):
            embed.add_field(
                name=f"{i+1:2d}번\t({search[i]['duration']}) {search[i]['channel']['name']}",
                value=f"제목: {search[i]['title']}",
                inline=False,
            )

        components = []

        for i in range(NUM_OF_SEARCH // 5 + 1):
            component = []
            for j in range(1, 6):
                if i * 5 + j - 1 == NUM_OF_SEARCH:
                    break
                component.append(Button(label=i * 5 + j, custom_id=f"{title}{i*5 + j}"))
            components.append(component)
        components[-1].append(
            Button(style=ButtonStyle.red, label="Cancel", custom_id=f"{title}c")
        )

        return embed, components

    @staticmethod
    def playlist():
        current_song_msg = "current_song_msg"
        next_songs_msg = "nex_songs_msg"

        embed = (
            discord.Embed(title="\u2000" * 5 + "Sky Whale", color=COLOR)
            .set_image(url=URL)
            .add_field(name=CURRENT_SONG_NAME, value=current_song_msg, inline=False)
            .add_field(name=NEXT_SONGS_NAME, value=next_songs_msg, inline=False)
            .set_footer(text="노래를 검색해서 추가하세요.")
        )

        components = [
            [
                Button(style=ButtonStyle.red, label="||", custom_id="pause"),
                Button(style=ButtonStyle.green, label="▶", custom_id="resume"),
                Button(style=ButtonStyle.blue, label="skip", custom_id="skip"),
                Button(style=ButtonStyle.grey, label="↻", custom_id="shuffle"),
                Button(style=ButtonStyle.grey, label="?", custom_id="help"),
            ],
            [
                Button(style=ButtonStyle.grey, label="<", custom_id="prev_page"),
                Button(style=ButtonStyle.grey, label=">", custom_id="next_page"),
                Button(style=ButtonStyle.grey, label="<<", custom_id="first_page"),
                Button(style=ButtonStyle.grey, label=">>", custom_id="last_page"),
                Button(style=ButtonStyle.grey, label="Youtube", custom_id="yt"),
            ],
        ]

        return embed, components


class Song:
    def __init__(self, id, title, url):
        self._id = id
        self._title = title
        self._url = url

    def __str__(self):
        return dict({"id": self._id, "title": self._title, "url": self._url})

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url


class Player:
    def __init__(self, playlist_channel):
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
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
        if self._voice["client"] and not self.voice["client"].is_paused():
            self._voice["client"].pause()

    def resume(self):
        if self._voice["client"] and self.voice["client"].is_paused():
            self._voice["client"].resume()

    def skip(self):
        pass

    async def play(self, message, song):
        if self._voice["client"] is None:
            await self._join(message.author.voice.channel)

        if self._playing:
            self._add_song(song)
            if not self._same_voice_channel(message.author.voice.channel):
                return await message.channel.send(
                    "노래를 추가했어요! 하지만 채널이 다르신 것 같아요.. 노래를 듣고싶다면 제가 있는 채널에 들어와주세요!"
                )

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
                after=lambda error: asyncio.get_event_loop().create_task(
                    self._check_queue()
                ),
            )
            self.pause()
            await asyncio.sleep(1)
            self.resume()
        except discord.opus.OpusNotLoaded:
            print(f"{song.title} play")
            await asyncio.sleep(10)
            print("play done")
            await self._check_queue()

    def _same_voice_channel(self, voice_channel):
        return self._voice["channel"] == voice_channel


class Youtube:
    NUM_OF_SEARCH = 9
    YDL_OPTS = {"format": "bestaudio/best", "quiet": True}

    @classmethod
    def extract_info(cls, link):
        with youtube_dl.YoutubeDL(cls.YDL_OPTS) as ydl:
            info = ydl.extract_info(url=link, download=False)

        return Song(id=info["id"], title=info["title"], url=info["formats"][3]["url"])

    @classmethod
    async def search(cls, title):
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: VideosSearch(title, limit=cls.NUM_OF_SEARCH)
        )

        return result.result()["result"]


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

        if "youtube.com" in message.content:
            link = message.content

        if "youtu.be" in message.content:
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
            await actions[interaction.custom_id]()

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

        player = Player(playlist_channel=channel)
        playlist_msg = await channel.send(embed=embed, components=components)
        player.set_playlist_msg(playlist_msg)
        self.players[channel.guild] = player

    async def _first(self, interaction):
        pass

    async def _next(self, interaction):
        pass

    async def _last(self, interaction):
        pass

    async def _pause(self, interaction):
        pass

    async def _prev(self, interaction):
        pass

    async def _resume(self, interaction):
        pass

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
        pass

    async def _skip(self, interaction):
        pass


def setup(bot):
    bot.add_cog(Playlist(bot))
