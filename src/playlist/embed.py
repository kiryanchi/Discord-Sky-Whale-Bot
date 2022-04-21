import re
import discord
from discord_components import Button, ButtonStyle

COLOR = 0x8AFDFD
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"
CURRENT_SONG_NAME: str = "현재 재생중인 노래"
NEXT_SONGS_NAME: str = "대기중인 노래"
NUM_OF_SEARCH = 9
SPACE = "\u17B5"


class Embed:
    @staticmethod
    def wrap(text):
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
    def _make_current_song_msg(player):
        return (
            player.songs["current"].title
            if player.songs["current"]
            else "재생중인 노래가 없습니다"
        )

    @staticmethod
    def _make_next_songs_msg(player):
        song_list = []
        try:
            for i in range(10 * player.current_page, 10 * (player.current_page + 1)):
                song_list.append(player.songs["next"][i].title)
        except IndexError:
            pass

        empty_song_list = ["예약된 노래가 없습니다." for i in range(10 - len(song_list))]

        song_list = [*song_list, *empty_song_list]

        next_songs_msg = ""

        for i in range(len(song_list)):
            tmp = Embed.wrap(text=song_list[i])
            next_songs_msg += f"> {SPACE}[{player.current_page * 10 + i + 1}] {tmp}\n"
        next_songs_msg += f"> {SPACE} \n> {SPACE} 현재 페이지 {player.current_page + 1} / {player.max_page + 1}"
        return next_songs_msg

    @staticmethod
    def playlist(player):
        async def callback(interaction):
            actions = {
                "first": player.first,
                "last": player.last,
                "next": player.next,
                "pause": player.pause,
                "prev": player.prev,
                "resume": player.resume,
                "shuffle": player.shuffle,
                "skip": player.skip,
                "yt": player.youtube,
            }
            await actions[interaction.custom_id](interaction)

        current_song_msg = Embed._make_current_song_msg(player)
        next_songs_msg = Embed._make_next_songs_msg(player)

        embed = (
            discord.Embed(title="\u2000" * 5 + "Sky Whale", color=COLOR)
            .set_image(url=URL)
            .add_field(name=CURRENT_SONG_NAME, value=current_song_msg, inline=False)
            .add_field(name=NEXT_SONGS_NAME, value=next_songs_msg, inline=False)
            .set_footer(text="노래를 검색해서 추가하세요.")
        )

        components_list = [
            [
                Button(style=ButtonStyle.red, label="||", custom_id="pause"),
                Button(style=ButtonStyle.green, label="▶", custom_id="resume"),
                Button(style=ButtonStyle.blue, label="skip", custom_id="skip"),
                Button(style=ButtonStyle.grey, label="↻", custom_id="shuffle"),
                Button(style=ButtonStyle.grey, label="?", custom_id="help"),
            ],
            [
                Button(style=ButtonStyle.grey, label="<<", custom_id="first"),
                Button(style=ButtonStyle.grey, label="<", custom_id="prev"),
                Button(style=ButtonStyle.grey, label=">", custom_id="next"),
                Button(style=ButtonStyle.grey, label=">>", custom_id="last"),
                Button(style=ButtonStyle.grey, label="Youtube", custom_id="yt"),
            ],
        ]

        components = [
            [
                player.bot.components_manager.add_callback(component, callback)
                for component in components
            ]
            for components in components_list
        ]

        return embed, components
