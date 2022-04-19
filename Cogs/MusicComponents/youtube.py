import asyncio
import youtube_dl
from youtubesearchpython import VideosSearch

from Cogs.MusicComponents.playlist_embed import PlaylistEmbed


class Youtube:
    def __init__(self, bot):
        self.bot = bot
        self.NUM_OF_SEARCH = 9
        self.YDL_OPTS = {"format": "bestaudio", "quiet": True}

    def extract_info(self, song):
        with youtube_dl.YoutubeDL(self.YDL_OPTS) as ydl:
            info = ydl.extract_info(song.link, download=False)
            mp3 = info["formats"][0]["url"]

        return mp3

    async def search_and_select(self, message):
        info: dict = await self.bot.loop.run_in_executor(
            None, lambda: self.search(message.content)
        )
        info = await self.select(message, info)

        return info

    def search(self, content):
        info = VideosSearch(content, limit=self.NUM_OF_SEARCH)

        return info.result()["result"]

    async def select(self, message, info):
        def check(interaction):
            return (
                message.author == interaction.user
                and message.content in interaction.custom_id
            )

        playlistEmbed = PlaylistEmbed()

        embed, components = playlistEmbed.search(message, info)

        msg = await message.reply(embed=embed, components=components)

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
            select = res.component.label
            if select == "Cancel":
                raise asyncio.exceptions.TimeoutError
            else:
                select = int(select)
        except asyncio.exceptions.TimeoutError or IndexError:
            await msg.delete()
            await message.channel.send("노래 선택이 취소되었습니다.", delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            return None

        await msg.delete()
        await message.delete()

        return info[select - 1]
