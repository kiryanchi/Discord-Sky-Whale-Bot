from discord import Embed, ui, ButtonStyle, Interaction

from setting import COLOR, NUM_OF_SEARCH, URL


class YoutubeEmbed(Embed):
    def __init__(self, song_title, result):
        super().__init__(title=f"{song_title} 검색 결과", color=COLOR)
        self.set_thumbnail(url=URL)

        for i in range(len(result)):
            self.add_field(
                name=f"{i+1:2d}번\t({result[i]['duration']}) {result[i]['channel']['name']}",
                value=f"제목: {result[i]['title']}",
                inline=False,
            )


class YoutubeView(ui.View):
    class Button(ui.Button["YoutubeView"]):
        def __init__(self, label, row):
            super().__init__(style=ButtonStyle.secondary, label=label, row=row)

        async def callback(self, interaction: Interaction):
            assert self.view is not None
            self.view.value = self.label

            self.view.stop()

    def __init__(self):
        super().__init__(timeout=15)
        self.value = None

        for i in range(NUM_OF_SEARCH // 5 + 1):
            for j in range(1, 6):
                if i * 5 + j - 1 == NUM_OF_SEARCH:
                    break
                self.add_item(
                    self.Button(
                        label=str(i * 5 + j),
                        row=i,
                    )
                )
