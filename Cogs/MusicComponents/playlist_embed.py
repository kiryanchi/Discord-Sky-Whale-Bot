import re
import discord
from discord_components import Button, ButtonStyle

COLOR = 0x8AFDFD
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"
CURRENT_SONG_NAME: str = "현재 재생중인 노래"
NEXT_SONGS_NAME: str = "대기중인 노래"

INIT_MSG = "```ansi\n[1;36m하늘 고래[0m가[1;34m 하늘[0m을 [1;35m향유[0m하기 시작했어요\n```"
NUM_OF_SEARCH = 9


class PlaylistEmbed:
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

    def init(self):
        embed = (
            discord.Embed(title="하늘 고래가 이 곳을 떠다니고 싶어합니다.", color=COLOR)
            .set_image(url=URL)
            .set_footer(text="수락을 누르면 이 채널을 음악 채널로 사용합니다.")
        )

        components = [
            Button(style=ButtonStyle.green, label="여기에 날아다니렴", custom_id="fly")
        ]

        return embed, components

    def search(self, message, info):
        NUM_OF_SEARCH = 9
        embed = discord.Embed(
            title=f"{message.content} 검색 결과", color=COLOR
        ).set_thumbnail(url=URL)

        for i in range(len(info)):
            embed.add_field(
                name=f"{i+1:2d}번\t({info[i]['duration']}) {info[i]['channel']['name']}",
                value=f"제목: {info[i]['title']}",
                inline=False,
            )

        components = []

        for i in range(NUM_OF_SEARCH // 5 + 1):
            component = []
            for j in range(1, 6):
                if i * 5 + j - 1 == NUM_OF_SEARCH:
                    break
                component.append(
                    Button(label=i * 5 + j, custom_id=f"{message.content}{i*5 + j}")
                )
            components.append(component)
        components[-1].append(
            Button(
                style=ButtonStyle.red, label="Cancel", custom_id=f"{message.content}c"
            )
        )

        return embed, components

    def playlist(self, playlist):
        current_song_msg = playlist.make_current_song_embed_message()
        next_songs_msg = playlist.make_next_songs_embed_message()

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
                Button(style=ButtonStyle.green, label="?", custom_id="resume"),
                Button(style=ButtonStyle.blue, label="?", custom_id="shuffle"),
                Button(style=ButtonStyle.blue, label="skip", custom_id="skip"),
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
