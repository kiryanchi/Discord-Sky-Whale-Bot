import asyncio
import youtube_dl
from youtubesearchpython import VideosSearch

from src.playlist.song import Song

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
