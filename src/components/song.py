import asyncio
from dataclasses import dataclass
from typing import Self

from discord import User
from yt_dlp import YoutubeDL

from setting import YTDLP_OPTS


@dataclass
class Song:
    title: str
    duration: str
    uploader: dict[str, str]
    view_count: str
    link: str
    thumbnail: str
    source: str
    user: User

    def __repr__(self):
        return self.title

    @property
    def is_playable(self) -> bool:
        return True if self.source else False

    @staticmethod
    async def download(link: str, user: User) -> Self:
        with YoutubeDL(YTDLP_OPTS) as ydl:
            meta = await asyncio.get_running_loop().run_in_executor(
                None, lambda: ydl.extract_info(url=link, download=False)
            )

        return Song(
            title=meta.get("title"),
            duration=meta.get("duration_string"),
            uploader={
                "name": meta.get("uploader"),
                "link": meta.get("uploader_url"),
            },
            view_count=format(meta.get("view_count"), ","),
            link=meta.get("webpage_url"),
            thumbnail=meta.get("thumbnail"),
            source=meta.get("url"),
            user=user,
        )
