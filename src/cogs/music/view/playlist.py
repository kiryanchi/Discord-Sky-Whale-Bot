import re

from discord import Embed, ui, ButtonStyle, Interaction

from setting import COLOR, URL
from src.tools import logger

CURRENT_SONG_NAME: str = "현재 재생중인 노래"
NEXT_SONGS_NAME: str = "대기중인 노래"
SPACE = "\u17B5"


class PlaylistEmbed(Embed):
    def __init__(self, player):
        self.player = player
        super().__init__(title="\u2000" * 5 + "Sky Whale", color=COLOR)
        self.set_image(url=self.current_image).add_field(
            name=CURRENT_SONG_NAME, value=self.current_song_message, inline=False
        ).add_field(
            name=NEXT_SONGS_NAME, value=self.next_song_message, inline=False
        ).set_footer(
            text="사용법은 ? 버튼을 눌러보세요"
        )

    @property
    def current_image(self):
        return self.player.current_song.thumbnail if self.player.current_song else URL

    @property
    def current_song_message(self):
        return (
            self.player.current_song.title
            if self.player.current_song
            else "재생중인 노래가 없습니다"
        )

    @property
    def next_song_message(self):
        song_list = []

        try:
            for i in range(
                10 * self.player.current_page, 10 * (self.player.current_page + 1)
            ):
                song_list.append(self.player.next_songs[i].title)
        except IndexError:
            pass

        empty_song_list = ["예약된 노래가 없습니다." for _ in range(10 - len(song_list))]

        song_list = [*song_list, *empty_song_list]

        next_songs_msg = ""

        for i in range(len(song_list)):
            tmp = self.wrap(text=song_list[i])
            next_songs_msg += (
                f"> {SPACE}[{self.player.current_page * 10 + i + 1}] {tmp}\n"
            )
        next_songs_msg += f"> {SPACE} \n> {SPACE} 현재 페이지 {self.player.current_page + 1} / {self.player.max_page + 1}"
        return next_songs_msg

    def wrap(self, text):
        def is_korean(character):
            hangul = re.compile("[^ㄱ-ㅣ가-힣]+")
            result = hangul.sub("", character)
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


class PlaylistView(ui.View):
    value = None

    class Button(ui.Button["PlaylistView"]):
        def __init__(self, style, label, custom_id, row):
            super().__init__(
                style=style,
                label=label,
                custom_id=custom_id,
                row=row,
            )

        async def callback(self, interaction: Interaction):
            assert self.view is not None

            actions = {
                "pause": self.view.player.pause,
                "resume": self.view.player.resume,
                "skip": self.view.player.skip,
                "shuffle": self.view.player.shuffle,
                "help": self.view.player.help,
                "first": self.view.player.first,
                "prev": self.view.player.prev,
                "next": self.view.player.next,
                "last": self.view.player.last,
                "yt": self.view.player.youtube,
            }
            logger.debug(f"Playlist.View.Button {interaction}")
            await actions[self.custom_id](interaction)

    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

        components_list = [
            [
                self.Button(
                    style=ButtonStyle.red, label="||", custom_id="pause", row=0
                ),
                self.Button(
                    style=ButtonStyle.green, label="▶", custom_id="resume", row=0
                ),
                self.Button(
                    style=ButtonStyle.blurple, label="skip", custom_id="skip", row=0
                ),
                self.Button(
                    style=ButtonStyle.grey, label="↻", custom_id="shuffle", row=0
                ),
                self.Button(style=ButtonStyle.grey, label="?", custom_id="help", row=0),
            ],
            [
                self.Button(
                    style=ButtonStyle.grey, label="<<", custom_id="first", row=1
                ),
                self.Button(style=ButtonStyle.grey, label="<", custom_id="prev", row=1),
                self.Button(style=ButtonStyle.grey, label=">", custom_id="next", row=1),
                self.Button(
                    style=ButtonStyle.grey, label=">>", custom_id="last", row=1
                ),
                self.Button(
                    style=ButtonStyle.grey, label="Youtube", custom_id="yt", row=1
                ),
            ],
        ]

        for components in components_list:
            for button in components:
                self.add_item(button)
