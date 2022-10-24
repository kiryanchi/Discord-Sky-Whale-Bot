import asyncio

from youtube_dl import YoutubeDL
from youtubesearchpython.__future__ import VideosSearch

from setting import NUM_OF_SEARCH
from src.cogs.music.components.song import Song

YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "no_warnings": True,
}


async def youtube_search(song_title):
    result = (await VideosSearch(song_title, limit=NUM_OF_SEARCH).next())["result"]
    return result


async def link_to_song(link):
    with YoutubeDL(YDL_OPTS) as ydl:
        info = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ydl.extract_info(url=link, download=False)
        )

    return Song(info)
