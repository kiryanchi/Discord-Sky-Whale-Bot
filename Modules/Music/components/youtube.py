import discord
import asyncio
import youtube_dl
from youtubesearchpython import VideosSearch
from discord_components import Button, ButtonStyle

from Modules.Music.utils.embeds import Embed


class Youtube:
    NUM_OF_SEARCH = 9
    YDL_OPTS = {"format": "bestaudio", "quiet": False}

    @classmethod
    def extract_info(cls, song):
        with youtube_dl.YoutubeDL(cls.YDL_OPTS) as ydl:
            info = ydl.extract_info(song.link, download=False)
            mp3 = info["formats"][0]["url"]

        return mp3

    @classmethod
    async def search_and_select(cls, app, message):
        info: dict = await app.loop.run_in_executor(
            None, lambda: cls.search(cls, message.content)
        )
        info = await cls.select(cls, app, message, info)

        return info

    def search(self, content):
        info = VideosSearch(content, limit=self.NUM_OF_SEARCH)

        return info.result()["result"]

    async def select(self, app, message, info):
        def check(interaction):
            return (
                message.author == interaction.user
                and message.content in interaction.custom_id
            )

        embed = Embed.search(message.content, info)

        components = []
        for i in range(self.NUM_OF_SEARCH // 5 + 1):
            component = []
            for j in range(1, 6):
                if i * 5 + j - 1 == self.NUM_OF_SEARCH:
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

        msg = await message.reply(embed=embed, components=components)

        try:
            res = await app.wait_for("button_click", check=check, timeout=15)
            select = res.component.label
            if select == "Cancel":
                raise TimeoutError
            else:
                select = int(select)
        except TimeoutError:
            await msg.delete()
            await message.channel.send("노래 선택이 취소되었습니다.", delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            return None

        await msg.delete()
        await message.delete()

        return info[select - 1]
