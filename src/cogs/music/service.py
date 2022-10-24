from discord import Interaction, Message, Guild

from setting import MUSIC_CHANNEL_NAME
from src.cogs.music.components.player import Player
from src.cogs.music.components.youtube import youtube_search, link_to_song
from src.cogs.music.view import YoutubeSearchResult
from src.tools import set_logger
from src.whale import Whale

log = set_logger()

INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"


class MusicService:
    def __init__(self, bot: Whale):
        self.bot = bot

    async def start_music_channel(self, interaction: Interaction):
        if interaction.channel.name != MUSIC_CHANNEL_NAME:
            log.info(
                f"길드: [{interaction.guild_id}/{interaction.guild.name}] :: {interaction.channel.name} 채널을 {MUSIC_CHANNEL_NAME} 로 변경했습니다."
            )
            await interaction.channel.edit(name=MUSIC_CHANNEL_NAME)

        await interaction.response.send_message(
            content="관리자 사용법", ephemeral=True
        )  # TODO: 사용법 설명하는 내용 작성

        await self.init_music_channel(interaction.guild, interaction.channel_id)

    async def init_music_channel(self, guild: Guild, channel_id: int):
        channel = guild.get_channel_or_thread(channel_id)

        if guild.id in self.bot.players:
            await self.bot.players[guild.id].leave()
            log.debug(f"길드: [{guild.id}/{guild.name}] :: 음성채널에서 봇 연결 끊음")

        await channel.purge()
        log.debug(f"길드: [{guild.id}/{guild.name}] :: {channel.name} 채널 퍼지")
        playlist = await channel.send(INIT_MSG)
        player = Player(
            bot=self.bot,
            playlist=playlist,  # TODO: Embed
        )
        # await playlist.edit(embed=Playlist.Embed(player))
        await player.update_playlist()
        self.bot.players[guild.id] = player
        log.info(f"길드: [{guild.id}/{guild.name}] :: 음악 채널을 초기화했습니다.")

    async def add_song_to_player(self, message: Message):
        # TODO: 로직 개선할 수 있지 않을까?
        link = None
        if "youtube.com" in message.content or "youtu.be" in message.content:
            link = message.content
        else:
            result = await youtube_search(message.content)

            view = YoutubeSearchResult.View(message)
            search_result_message = await message.channel.send(
                embed=YoutubeSearchResult.Embed(message.content, result),
                view=view,
                delete_after=15,
            )

            await view.wait()

            if view.value is None:
                # await message.delete()
                return await message.delete()

            await search_result_message.delete()
            link = result[int(view.value) - 1]["link"]

        song = await link_to_song(link)
        log.info(f"길드: [{message.guild.id}/{message.guild.name}] :: 노래 {song} 검색")

        # TODO: player에 song 집어넣기
        await message.delete()
        await self.bot.players[message.guild.id].play(message, song)
