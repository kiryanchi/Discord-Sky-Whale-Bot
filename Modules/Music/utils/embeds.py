import discord
from Modules.Music.components.song import Song
from Modules.Music.components.queue import Queue


COLOR = 0x8AFDFD
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"


class Embed:
    @staticmethod
    def init() -> discord.Embed:
        embed = (
            discord.Embed(title="하늘 고래가 이 곳을 떠다니고 싶어합니다.", color=COLOR)
            .set_image(url=URL)
            .set_footer(text="수락을 누르면 이 채널을 음악 채널로 사용합니다.")
        )
        return embed

    @staticmethod
    def playlist(song: Song, queue: Queue, thumbnail: str = URL) -> discord.Embed:
        embed = (
            discord.Embed(title="\u2000" * 5 + "Sky Whale", color=COLOR)
            .add_field(name=song.title, value=song., inline=False)
            .set_thumbnail(url=thumbnail)
            .add_field(name="대기중인 곡", value=queue, inline=False)
            .set_footer(text="노래를 검색해서 추가하세요.")
        )

        if song:


        return embed
