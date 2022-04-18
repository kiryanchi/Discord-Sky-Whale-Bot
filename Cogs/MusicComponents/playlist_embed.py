import discord
import re
from discord_components import Button, ButtonStyle


COLOR = 0x8AFDFD
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"
CURRENT_SONG_NAME: str = "현재 재생중인 노래"
NEXT_SONGS_NAME: str = "대기중인 노래"


class PlaylistEmbed:
    def __init__(self, bot):
        self.bot = bot

    def __wrap(self, text):
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

    async def init(self, ctx):
        async def init_callback(interaction):
            await interaction.send(content="init")
            print("do this?")

        embed = (
            discord.Embed(title="하늘 고래가 이 곳을 떠다니고 싶어합니다.", color=COLOR)
            .set_image(url=URL)
            .set_footer(text="수락을 누르면 이 채널을 음악 채널로 사용합니다.")
        )

        components = [
            self.bot.components_manager.add_callback(
                Button(style=ButtonStyle.green, label="여기에 날아다니렴")
            )
        ]

        await ctx.send(embed=embed, components=components)
        print("this do")

    def search(self, content, info):
        embed = discord.Embed(title=f"{content} 검색 결과", color=COLOR).set_thumbnail(
            url=URL
        )

        for i in range(len(info)):
            embed.add_field(
                name=f"{i+1:2d}번\t({info[i]['duration']}) {info[i]['channel']['name']}",
                value=f"제목: {info[i]['title']}",
                inline=False,
            )

        return embed

    def playlist(self, current_song, next_songs):
        # TODO: 아직 미완성

        embed = (
            discord.Embed(title="\u2000" * 5 + "Sky Whale", color=COLOR)
            .set_image(url=URL)
            .add_field(name=CURRENT_SONG_NAME, value=current_song, inline=False)
            .add_field(name=NEXT_SONGS_NAME, value=next_songs, inline=False)
            .set_footer(text="노래를 검색해서 추가하세요.")
        )

        return embed
